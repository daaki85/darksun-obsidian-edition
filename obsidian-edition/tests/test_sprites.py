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
        gear, _ = sprites.worn(Worn([item(28, 0, right)]), 0)  # (Shillelagh, no plus: a spell's)
        self.assertEqual(gear["right"][2], sg.MAGIC)
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
        dresser.items = chunks
        dresser.store, dresser._built, dresser.reused = sprites.Store(dresser.gd), {}, 0
        return dresser, path

    def test_never_past_the_copys_room(self):
        """Pictures reckoning more room than the copy kept (written with the other LOOKS, the
        switch changed and the Loader connected again): what is written fits the copy's own room
        (gff.rooms), the plain picture if the dressed one wouldn't, and the chunks after it are
        untouched."""
        outfits = [({"right": (SWORD, METAL), "cloak": (65, 5), "boots": (68, 5)}, (57,))]
        worn, sprites.worn = sprites.worn, lambda gd, member, chunks=None: outfits[0]
        self.addCleanup(setattr, sprites, "worn", worn)
        with tempfile.TemporaryDirectory() as d:
            dresser, path = self.dressed_copy(d)
            before = read(path)
            walk, fight = sprites.picture_ids(300)
            rooms = gff.rooms(before, "BMP ")
            places = gff.index_places(before, "BMP ")
            dressed = dresser.pics.build(300, False, *outfits[0])
            plain = dresser.pics.build(300, False, {}, ())
            self.assertGreater(len(dressed), len(plain))
            # (the copy's room for the walking picture: just the plain one's)
            real_rooms = gff.rooms
            gff.rooms = lambda data, ctype: {**real_rooms(data, ctype), walk: len(plain)}
            self.addCleanup(setattr, gff, "rooms", real_rooms)
            dresser.pics.room = lambda obj, combat: 1 << 20  # (Pictures overstating it)
            dresser.gd.entry(0, walk, 7)
            dresser.update(True, 1.0)
            after = read(path)
            _, offset, length = gff.index_places(after, "BMP ")[walk]
            self.assertLessEqual(length, len(plain))
            end = places[walk][1] + rooms[walk]
            self.assertEqual(after[offset + len(plain):end], before[offset + len(plain):end])

    def test_rooms(self):
        """gff.rooms: from each chunk's start to the next chunk's, of any type, or the index."""
        from test_core import build_gff
        data = build_gff({("BMP ", 1): b"a" * 10, ("OJFF", 5): b"b" * 4, ("BMP ", 2): b"c" * 7})
        places = gff.index_places(data, "BMP ")
        out = gff.rooms(data, "BMP ")
        for cid in (1, 2):
            self.assertGreaterEqual(out[cid], places[cid][2])
            starts = [o for _, o, _ in list(gff.index_places(data, "BMP ").values()) + list(gff.index_places(data, "OJFF").values())]
            later = [s for s in starts if s > places[cid][1]]
            if later:
                self.assertEqual(out[cid], min(later) - places[cid][1])

    def test_items_from_the_copy(self):
        """The Loader's own items (a Hayneedle, object 2590) are only in its copy of SEGOBJEX: the
        glow looks their objects and icons up there, the game's file's for the rest."""
        from test_core import build_gff
        with tempfile.TemporaryDirectory() as d:
            chunks = game_chunks()
            own = os.path.join(d, "GAME.GFF")
            with open(own, "wb") as f:
                f.write(build_gff(chunks))
            copy = os.path.join(d, "SEGOBJEX.GFF")
            with open(copy, "wb") as f:
                f.write(build_gff({("OJFF", 2590): b"hayneedle"}))
            dresser = sprites.Dresser(FakeGame(figures=[0]), own, [(0, 0, 0)] * 256, copy)
            self.assertEqual(dresser.items[("OJFF", 2590)], b"hayneedle")
            self.assertEqual(dresser.items[("OJFF", 300)], chunks[("OJFF", 300)])
            self.assertNotIn(("OJFF", 2590), dresser.pics.chunks)
            plain = sprites.Dresser(FakeGame(figures=[0]), own, [(0, 0, 0)] * 256)
            self.assertIs(plain.items, plain.pics.chunks)

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

    def test_no_room_in_the_games_store(self):
        """An outfit changed while the game's store of pictures (or its table) has no room for it
        loaded anew: left as it was, nothing taken out of the game's table, tried again once there
        is room (an area loaded)."""
        outfits = [({"right": (SWORD, METAL)}, ())]
        worn, sprites.worn = sprites.worn, lambda gd, member, chunks=None: outfits[0]
        self.addCleanup(setattr, sprites, "worn", worn)
        with tempfile.TemporaryDirectory() as d:
            dresser, path = self.dressed_copy(d)
            gd = dresser.gd
            walk, fight = sprites.picture_ids(300)
            gd.entry(0, walk, 7)
            gd.loaded([1234, walk, fight, 99])
            self.assertEqual(dresser.update(True, 1.0), [300])  # (the first dressing: always)
            gd.entry(0, walk, 8)
            gd.loaded([1234, walk, fight, 99])
            base = (gd.load_seg + sprites.PICTURE_TABLE_SEG) * 16 + 3 * sprites.PICTURE_ENTRY
            gd.guest.write(base + sprites.SLOT_LENGTH, struct.pack("<Ii", 5000, sprites.STORE_SIZE - 6000))
            outfits[0] = ({}, ())
            self.assertEqual(dresser.update(True, 2.0), [])
            self.assertEqual(gd.loaded_numbers(), [1234, walk, fight, 99])
            self.assertEqual(gd.entry_fields(0), (walk, 8))
            gd.guest.write(base + sprites.SLOT_LENGTH, struct.pack("<Ii", 5000, 100000))
            self.assertEqual(dresser.update(True, 3.0), [300])
            self.assertEqual(gd.loaded_numbers(), [1234, sprites.STALE, sprites.STALE, 99])
            gd.loaded(list(range(sprites.PICTURES_MOST - sprites.SLOTS_SPARE - 1)))
            outfits[0] = ({"right": (SWORD, METAL)}, ())
            self.assertEqual(dresser.update(True, 4.0), [])  # (the table nearly full)

    # The game's picture store reused (sprites.Store, Dresser._in_store): FakeGame.xms
    NOISE = bytes((i * 37 + 11) & 0xFF for i in range(256))  # (a picture of the game's, in memory)
    A, B = ({"right": (SWORD, METAL)}, ()), ({}, ())

    def store_dresser(self, d, outfits, backend_write=None):
        """A Dresser (dressed_copy) whose game has the XMS store and a picture of its own in
        memory (slot 0); the member dressed once in OUTFITS[0] with nothing loaded. (dresser, its
        game, walk, fight, {outfit: its walking chunk})."""
        worn, sprites.worn = sprites.worn, lambda gd, member, chunks=None: outfits[0]
        self.addCleanup(setattr, sprites, "worn", worn)
        dresser, path = self.dressed_copy(d)
        gd = dresser.gd
        gd.xms(backend_write)
        walk, fight = sprites.picture_ids(300)
        gd.entry(0, walk, 7)
        self.assertEqual(dresser.update(True, 1.0), [300])  # (the first dressing: nothing loaded)
        chunks = {}
        for outfit in (self.A, self.B):
            outfits[0] = outfit
            dresser.shown.clear()
            dresser.update(True, 1.0)
            chunks[repr(outfit)] = dresser._built[300][1][walk]
        outfits[0] = self.A
        dresser.shown.clear()
        dresser.update(True, 1.0)
        self.assertNotEqual(chunks[repr(self.A)], chunks[repr(self.B)])
        gd.slot(0, 1234, self.NOISE, in_memory=True)
        return dresser, gd, walk, fight, chunks

    def test_store_found(self):
        """The store found where DOSBox has it (the handle, the page directory, the XMS backend,
        an in-memory picture's bytes), and refused when anything is otherwise: another backend, no
        picture in memory to find it by, bytes that don't match, a page not in the directory, the
        handle's id not the table's, another picture in memory not where the pages put it (the
        block not in one piece); once found, refused again if its bytes are no longer there."""
        def found(gd):
            dresser = sprites.Dresser.__new__(sprites.Dresser)
            dresser.gd = gd
            store = sprites.Store(gd)
            return store.locate(dresser._slots()), store, dresser
        gd = FakeGame(figures=[0])
        gd.xms()
        self.assertFalse(found(gd)[0])  # (nothing in memory)
        gd.slot(0, 1234, self.NOISE, in_memory=True)
        ok, store, dresser = found(gd)
        self.assertTrue(ok)
        self.assertEqual(store.base, FakeGame.XMS_BASE)
        self.assertEqual(store.read(0x4000 - 8, 16), gd.guest.read(gd.store_at(0x4000 - 8), 16))  # (across a page)
        gd.guest.write(gd.store_at(0), b"\0" * 64)  # (moved, or not the store's: refused)
        self.assertFalse(store.locate(dresser._slots()))
        for spoil in ("backend", "match", "directory", "handle", "scattered"):
            gd = FakeGame(figures=[0])
            gd.xms(0x12340000 if spoil == "backend" else None)
            gd.slot(0, 1234, self.NOISE, in_memory=True)
            if spoil == "match":
                gd.guest.write(gd.store_at(0), bytes(len(self.NOISE)))
            elif spoil == "directory":
                gd.guest.write(gd.ds * 16 + sprites.DIR_BLOCKS + 2, struct.pack("<HH", 2, 0))
            elif spoil == "handle":
                gd.guest.write(gd.ds * 16 + sprites.HANDLES + 2, struct.pack("<H", 0x1111))
            elif spoil == "scattered":
                gd.slot(3, 999, self.NOISE[::-1] * 4, length=1024, in_memory=True)
                gd.guest.write(gd.store_at(3 * 0x5000 + 1024 - 16), bytes(16))  # (its end elsewhere)
            self.assertFalse(found(gd)[0], spoil)

    def test_same_chunk_given_its_number_back(self):
        """An outfit changed back: the STALE slot holding just that picture given its number back
        (nothing written, no new slot), the other made STALE. With no cell to be had (the old
        picture in memory), the old way: STALE, a new slot for the game."""
        outfits = [self.A]
        with tempfile.TemporaryDirectory() as d:
            dresser, gd, walk, fight, chunks = self.store_dresser(d, outfits)
            a, b = chunks[repr(self.A)], chunks[repr(self.B)]
            gd.slot(1, walk, a, in_memory=True)
            outfits[0] = self.B
            self.assertEqual(dresser.update(True, 2.0), [300])
            self.assertEqual(gd.loaded_numbers(), [1234, sprites.STALE])  # (the old way)
            self.assertEqual(dresser.reused, 0)
            gd.slot(2, walk, b, in_memory=True)  # (the game loads it into a new slot)
            outfits[0] = self.A
            self.assertEqual(dresser.update(True, 3.0), [300])
            self.assertEqual(gd.loaded_numbers(), [1234, walk, sprites.STALE])
            self.assertEqual(dresser.reused, 1)
            self.assertEqual((gd.stored(1, len(a)), gd.in_memory(1, len(a))), (a, a))
            self.assertEqual(gd.entry_fields(0), (walk, sprites.NO_SLOT))  # (drawn from it at once)

    def test_own_slot_written_where_it_is(self):
        """The picture's own slot out of memory with room (the inventory open): the new picture
        written into the store at its place, its number and length kept, no new slot."""
        outfits = [self.A]
        with tempfile.TemporaryDirectory() as d:
            dresser, gd, walk, fight, chunks = self.store_dresser(d, outfits)
            b = chunks[repr(self.B)]
            gd.slot(1, walk, chunks[repr(self.A)], in_memory=False)
            outfits[0] = self.B
            self.assertEqual(dresser.update(True, 2.0), [300])
            self.assertEqual(gd.loaded_numbers(), [1234, walk])
            self.assertEqual(gd.stored(1, len(b)), b)
            base = (gd.load_seg + sprites.PICTURE_TABLE_SEG) * 16 + sprites.PICTURE_ENTRY
            self.assertEqual(struct.unpack("<I", gd.guest.read(base + sprites.SLOT_LENGTH, 4))[0], 20000)
            self.assertEqual(dresser.reused, 1)

    def test_store_written_under_the_item_gates_hold(self):
        """DOSBox paused while the store is written, and let go after; when the item gate already
        holds it (a block of item writes open) neither paused nor let go here: still the gate's."""
        from dsloader import itemgate

        class Proc:
            def __init__(self):
                self.calls = []

            def suspend(self):
                self.calls.append("suspend")
                return True

            def resume(self):
                self.calls.append("resume")
        for held in (False, True):
            outfits = [self.A]
            with tempfile.TemporaryDirectory() as d:
                dresser, gd, walk, fight, chunks = self.store_dresser(d, outfits)
                proc = gd.guest.proc = Proc()
                if held:
                    itemgate._HELD.add(proc)
                    self.addCleanup(itemgate._HELD.discard, proc)
                gd.slot(1, walk, chunks[repr(self.A)], in_memory=False)
                outfits[0] = self.B
                self.assertEqual(dresser.update(True, 2.0), [300])
                self.assertEqual(dresser.reused, 1)
                self.assertEqual(proc.calls, [] if held else ["suspend", "resume"], held)
                self.assertEqual(proc in itemgate._HELD, held)

    def test_room_for_counts_the_furthest_slot(self):
        """The room left in the game's store: past the furthest slot's end, not the last slot's (the
        game may have put the last in a hole); a slot with no place (-1) not counted."""
        gd = FakeGame(figures=[0])
        dresser = sprites.Dresser.__new__(sprites.Dresser)
        dresser.gd = gd
        gd.loaded([1, 2, 3, 4])
        base = (gd.load_seg + sprites.PICTURE_TABLE_SEG) * 16
        for k, (length, place) in enumerate(((1000, 0), (5000, sprites.STORE_SIZE - 6000), (100, -1), (100, 1000))):
            gd.guest.write(base + k * sprites.PICTURE_ENTRY + sprites.SLOT_LENGTH, struct.pack("<Ii", length, place))
        self.assertFalse(dresser._room_for(2000))
        gd.guest.write(base + sprites.PICTURE_ENTRY + sprites.SLOT_LENGTH, struct.pack("<Ii", 5000, 2000))
        self.assertTrue(dresser._room_for(2000))
        gd.loaded([])
        self.assertTrue(dresser._room_for(2000))

    def test_smallest_stale_cell_with_room(self):
        """A new picture whose own slot is in memory: written into the smallest STALE slot out of
        memory with room for it, given its number; the old slot made STALE. A picture in memory
        (the old one, a STALE one) never written; one too small never used."""
        outfits = [self.A]
        with tempfile.TemporaryDirectory() as d:
            dresser, gd, walk, fight, chunks = self.store_dresser(d, outfits)
            a, b = chunks[repr(self.A)], chunks[repr(self.B)]
            x, y = bytes([7]) * 20000, bytes([9]) * 20000
            gd.slot(1, walk, a, in_memory=True)
            gd.slot(2, sprites.STALE, x, length=len(b), in_memory=True)  # (the best fit, but in memory)
            gd.slot(3, sprites.STALE, y, length=len(b) - 1)
            gd.slot(4, sprites.STALE, y, length=19000)
            gd.slot(5, sprites.STALE, y, length=15000)
            outfits[0] = self.B
            self.assertEqual(dresser.update(True, 2.0), [300])
            self.assertEqual(gd.loaded_numbers(), [1234, sprites.STALE, sprites.STALE, sprites.STALE, sprites.STALE, walk])
            self.assertEqual(gd.stored(5, len(b)), b)
            self.assertEqual((gd.stored(1, len(a)), gd.in_memory(1, len(a))), (a, a))
            self.assertEqual((gd.stored(2, 20000), gd.in_memory(2, 20000)), (x, x))
            self.assertEqual((gd.stored(3, len(b)), gd.stored(4, len(b))), (y[:len(b)], y[:len(b)]))

    def test_a_cell_needs_no_room(self):
        """With the table nearly full a dressing that finds cells for both its pictures goes ahead
        (no new slot); one that would need a new slot is left as it was (_room_for)."""
        outfits = [self.A]
        with tempfile.TemporaryDirectory() as d:
            dresser, gd, walk, fight, chunks = self.store_dresser(d, outfits)
            gd.loaded(list(range(sprites.PICTURES_MOST - sprites.SLOTS_SPARE)))
            gd.slot(0, 1234, self.NOISE, in_memory=True)
            gd.slot(1, walk, chunks[repr(self.A)])
            gd.slot(2, fight, bytes(100))
            outfits[0] = self.B
            self.assertEqual(dresser.update(True, 2.0), [300])
            self.assertEqual(gd.loaded_numbers()[:3], [1234, walk, fight])
            self.assertEqual(dresser.reused, 2)
            gd.slot(1, walk, chunks[repr(self.B)], in_memory=True)  # (no cell for it now)
            outfits[0] = self.A
            self.assertEqual(dresser.update(True, 3.0), [])
            self.assertEqual(gd.loaded_numbers()[:3], [1234, walk, fight])

    def test_no_store_the_old_way(self):
        """The store not as DOSBox has it (another backend, or its bytes not found: the
        recompiled program's): the old way, the old pictures STALE for the game to load anew."""
        for spoil in ("backend", "match"):
            outfits = [self.A]
            with tempfile.TemporaryDirectory() as d:
                dresser, gd, walk, fight, chunks = self.store_dresser(
                    d, outfits, 0x12340000 if spoil == "backend" else None)
                if spoil == "match":
                    gd.guest.write(gd.store_at(0), bytes(len(self.NOISE)))
                a = chunks[repr(self.A)]
                gd.slot(1, walk, a)
                outfits[0] = self.B
                self.assertEqual(dresser.update(True, 2.0), [300], spoil)
                self.assertEqual(gd.loaded_numbers(), [1234, sprites.STALE], spoil)
                self.assertEqual((gd.stored(1, len(a)), dresser.reused), (a, 0), spoil)

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
        self.mem = bytearray(0x200000)  # (1 MB and the XMS block past it: FakeGame.xms)
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

    XMS_BASE, FIRST_PAGE, MEMORY = 0x110000, 2, 0x60000

    def xms(self, backend_write=None):
        """The game's store as DOSBox has it: handle 0 (id 48EFh) of STORE_SIZE bytes, its pages a
        chain in the first page directory block, on backend 0 (the XMS write, or BACKEND_WRITE),
        XMS pages FIRST_PAGE on at XMS_BASE."""
        d = self.ds * 16
        self.guest.write(d + sprites.STORE_HANDLE, struct.pack("<I", 0x48EF0000))
        self.guest.write(d + sprites.HANDLES, struct.pack("<HHI", self.FIRST_PAGE, 0x48EF, sprites.STORE_SIZE))
        block = d + sprites.DIR_BLOCKS
        self.guest.write(block + 2, struct.pack("<HH", 1, 0))
        pages = (sprites.STORE_SIZE + sprites.STORE_PAGE - 1) // sprites.STORE_PAGE
        for n in range(pages):
            link = self.FIRST_PAGE + n
            self.guest.write(block + sprites.DIR_ENTRIES + link * 4, struct.pack("<HH", link, link + 1))
        write = backend_write if backend_write is not None else \
            (self.load_seg + sprites.XMS_WRITE[0]) << 16 | sprites.XMS_WRITE[1]
        self.guest.write(d + sprites.BACKEND_WRITE, struct.pack("<I", write))

    def store_at(self, place):
        return self.XMS_BASE + self.FIRST_PAGE * sprites.STORE_PAGE + place

    def slot(self, k, number, data, length=20000, in_memory=False):
        """Slot K of the picture table: NUMBER, its LENGTH, its place k * 5000h in the store holding
        DATA; IN_MEMORY, also at its far pointer (MEMORY + k * 5000h)."""
        base = (self.load_seg + sprites.PICTURE_TABLE_SEG) * 16 + k * sprites.PICTURE_ENTRY
        far = self.MEMORY + k * 0x5000
        self.guest.write(base, struct.pack("<HIiHHBB", number, length, k * 0x5000, far & 0xF, far >> 4,
                                           1 | (sprites.IN_MEMORY if in_memory else 0), 255))
        self.guest.write(self.store_at(k * 0x5000), data)
        if in_memory:
            self.guest.write(far, data)
        count, = struct.unpack("<H", self.guest.read(self.ds * 16 + sprites.PICTURE_COUNT, 2))
        self.guest.write(self.ds * 16 + sprites.PICTURE_COUNT, struct.pack("<H", max(count, k + 1)))

    def stored(self, k, n):
        return self.guest.read(self.store_at(k * 0x5000), n)

    def in_memory(self, k, n):
        return self.guest.read(self.MEMORY + k * 0x5000, n)

    def entry_fields(self, combatant):
        at = self.ds * 16 + sprites.MAP_ENTRIES + combatant * sprites.MAP_ENTRY_SIZE
        return (struct.unpack("<H", self.guest.read(at + sprites.MAP_PICTURE, 2))[0],
                struct.unpack("<H", self.guest.read(at + sprites.MAP_SLOT, 2))[0])


if __name__ == "__main__":
    unittest.main()
