"""The sequel's talk portraits at Shattered Lands' size (ravportraits): a made-up 72 by 72 face cut to a 48 by 46
frame round a 32 by 32 face, the empty frame's two pictures, the talk window 58 high with its text at x 58,
the patches' bytes; with DSUN_WOTR the player's files: every face made smaller, the patches matching the
game's DSUN.EXE, and the Loader's copies holding them (none with the control's SKIP)."""

import os
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import art, gff, ravager, ravportraits as rp, wotrart  # noqa: E402

WOTR = os.environ.get("DSUN_WOTR")
SL = os.environ.get("DSUN_SL")


def sequel_face(face_colour=50, border=200):
    """A sequel PORT's rows: 72 by 72, the frame BORDER (its corners 0), the face 56 by 58 at (8, 7)."""
    rows = [[border] * 72 for _ in range(72)]
    rows[0][0] = rows[0][71] = rows[71][0] = rows[71][71] = 0
    for y in range(7, 65):
        for x in range(8, 64):
            rows[y][x] = face_colour + (x + y) % 3
    return rows


def size(chunk, index=0):
    offset, = struct.unpack_from("<I", chunk, 6 + 4 * index)
    return struct.unpack_from("<HH", chunk, offset)


class ShapeTests(unittest.TestCase):
    def test_the_frame_is_cut_down_round_a_clear_middle(self):
        rows = rp.frame(sequel_face())
        self.assertEqual((len(rows[0]), len(rows)), (rp.WIDTH, rp.HEIGHT))
        self.assertEqual((rp.WIDTH, rp.HEIGHT), (48, 46))
        self.assertEqual(rows[0][0], 0)  # (the corners kept)
        self.assertEqual(rows[rp.HEIGHT - 1][rp.WIDTH - 1], 0)
        self.assertEqual(rows[rp.TOP][rp.LEFT], 0)  # (the face's place clear)
        self.assertEqual(rows[rp.TOP][rp.LEFT - 1], 200)
        self.assertEqual(rows[rp.TOP + rp.FACE][rp.LEFT], 200)

    def test_a_face_made_smaller_keeps_its_own_colours(self):
        palette = [(i, i, i) for i in range(256)]
        chunk = art.plnr_frames([sequel_face()])
        out = wotrart.decode_plnr(rp.portrait(chunk, rp.frame(sequel_face()), palette))
        self.assertEqual((len(out[0]), len(out)), (48, 46))
        face = {p for r in out[rp.TOP:rp.TOP + rp.FACE] for p in r[rp.LEFT:rp.LEFT + rp.FACE]}
        self.assertTrue(face <= {50, 51, 52})
        self.assertEqual(out[1][1], 200)

    def test_without_a_palette_the_middle_pixel(self):
        rows = sequel_face()
        small = rp.smaller(rows, 8, 8, 56, None)
        self.assertEqual((len(small), len(small[0])), (32, 32))

    def test_every_face_made_smaller_once(self):
        chunks = {("PORT", n): art.plnr_frames([sequel_face(40 + n)]) for n in (1, 2, 3)}
        out = rp.script_chunks(chunks)
        self.assertEqual(set(out), set(chunks))
        self.assertTrue(all(size(c) == (48, 46) for c in out.values()))
        self.assertEqual(rp.script_chunks(out), {})  # (already small: left)


class WindowTests(unittest.TestCase):
    def window(self, height=72, x=75):
        head = bytearray(rp.ITEM_AT)
        struct.pack_into("<H", head, rp.WIND_HEIGHT, height)
        struct.pack_into("<H", head, rp.WIND_COUNT, 2)
        items = bytes(4) + b"BUTN" + struct.pack("<IHH", 12300, 0, 0) + bytes(rp.ITEM_SIZE - 16)
        items += bytes(4) + b"EBOX" + struct.pack("<IHH", rp.TEXT_BOX, x, 6) + bytes(rp.ITEM_SIZE - 16)
        return bytes(head) + items

    def test_the_talk_window_as_shattered_lands(self):
        out = rp.talk_window(self.window())
        self.assertEqual(struct.unpack_from("<H", out, rp.WIND_HEIGHT)[0], 58)
        self.assertEqual(struct.unpack_from("<IHH", out, rp.ITEM_AT + rp.ITEM_SIZE + 8), (rp.TEXT_BOX, 58, 6))
        self.assertEqual(struct.unpack_from("<IHH", out, rp.ITEM_AT + 8), (12300, 0, 0))

    def shop(self, sell=(277, 159), more=(235, 159)):
        head = bytearray(rp.ITEM_AT)
        struct.pack_into("<H", head, rp.WIND_COUNT, 3)
        items = b""
        for tag, n, (x, y) in ((b"BUTN", 13304, sell), (b"BUTN", 13303, more), (b"APFM", 11242, (245, 80))):
            items += bytes(4) + tag + struct.pack("<IHH", n, x, y) + bytes(rp.ITEM_SIZE - 16)
        return bytes(head) + items

    def test_the_shop_buttons_as_shattered_lands(self):
        out = rp.shop_window(self.shop())
        at = rp.ITEM_AT + 8
        self.assertEqual(struct.unpack_from("<IHH", out, at), (13304, 255, 59))  # (SELL under the face)
        self.assertEqual(struct.unpack_from("<IHH", out, at + rp.ITEM_SIZE), (13303, 255, 159))  # (MORE alone)
        self.assertEqual(struct.unpack_from("<IHH", out, at + 2 * rp.ITEM_SIZE), (11242, 245, 80))  # (the list kept)
        self.assertIsNone(rp.shop_window(out))  # (already moved: left)
        self.assertIsNone(rp.shop_window(self.shop(sell=(1, 2))))

    def test_the_empty_frame_round_the_emblem(self):
        resource = {rp.EMPTY_FRAME: art.plnr_frames([sequel_face(), sequel_face(90)])}
        sun = [[7] * rp.FACE for _ in range(rp.FACE)]
        empty = rp.empty_frame(resource, {("PORT", 1): art.plnr_frames([sequel_face()])}, None, sun)
        washed = rp._frame_rows(empty, 1)
        self.assertEqual({p for r in washed[rp.TOP:rp.TOP + rp.FACE] for p in r[rp.LEFT:rp.LEFT + rp.FACE]}, {7})
        self.assertEqual(washed[1][1], 200)

    def test_the_empty_frame_has_both_pictures(self):
        clear = sequel_face()
        for y in range(7, 65):
            clear[y][8:64] = [0] * 56
        washed = sequel_face(90)
        resource = {rp.EMPTY_FRAME: art.plnr_frames([clear, washed]), ("WIND", rp.TALK_WINDOW): self.window(),
                    rp.PALETTE: bytes(768), ("WIND", rp.SHOP_WINDOW): self.shop()}
        out = rp.resource_chunks(resource, {("PORT", 1): art.plnr_frames([sequel_face()])})
        empty = out[rp.EMPTY_FRAME]
        self.assertEqual(struct.unpack_from("<H", empty, 4)[0], 2)
        self.assertEqual((size(empty, 0), size(empty, 1)), ((48, 46), (48, 46)))
        self.assertEqual(out[("WIND", rp.SHOP_WINDOW)], rp.shop_window(self.shop()))
        self.assertEqual(rp.resource_chunks(resource, None), {})
        self.assertEqual(rp.resource_chunks({**resource, ("WIND", rp.TALK_WINDOW): self.window(58)},
                                            {("PORT", 1): art.plnr_frames([sequel_face()])}), {})


class PatchTests(unittest.TestCase):
    def test_the_patches(self):
        names = {p.name for p in ravager.PATCHES}
        self.assertTrue(rp.PATCH_NAMES <= names)
        for p in rp.PATCHES:
            self.assertEqual(len(p.original), len(p.replacement), p.name)
        at = next(p for p in rp.PATCHES if p.name == "small_portraits_at")
        self.assertEqual(at.replacement, bytes.fromhex("bf0800c646fe06"))  # (mov di,8 / mov byte [bp-2],6)
        self.assertEqual((rp.SHOP_X, rp.SHOP_Y), (252, 11))  # (Shattered Lands' frame in its shop)
        shop = next(p for p in rp.PATCHES if p.name == "small_portraits_shop")
        self.assertEqual(shop.replacement, bytes.fromhex("bffc00c746fe0b00"))


@unittest.skipUnless(WOTR, "DSUN_WOTR not set (the sequel's own files)")
class GameFileTests(unittest.TestCase):
    def test_the_game_files(self):
        with open(os.path.join(WOTR, "DSUN.EXE"), "rb") as f:
            exe = f.read()
        for p in rp.PATCHES:
            self.assertEqual(exe[p.offset:p.offset + len(p.original)], p.original, p.name)
        with tempfile.TemporaryDirectory() as tmp:
            scripts, resources = os.path.join(tmp, ravager.SCRIPT_COPY), os.path.join(tmp, ravager.RESOURCE_COPY)
            self.assertIn(rp.SKIP, ravager.write_scripts(WOTR, scripts))
            self.assertIn(rp.SKIP, ravager.write_resources(WOTR, resources))
            with open(scripts, "rb") as f:
                faces = {k: v for k, v in gff.read_gff(f.read()).items() if k[0] == "PORT"}
            self.assertGreater(len(faces), 100)
            self.assertTrue(all(size(c) == (48, 46) for c in faces.values()))
            with open(resources, "rb") as f:
                res = gff.read_gff(f.read())
            self.assertEqual(struct.unpack_from("<H", res[("WIND", rp.TALK_WINDOW)], rp.WIND_HEIGHT)[0], 58)
            self.assertIsNone(rp.shop_window(res[("WIND", rp.SHOP_WINDOW)]))  # (SELL and MORE already moved)
            if SL:  # (Shattered Lands' emblem in the empty frame)
                ravager.write_resources(WOTR, resources, set(), SL)
                with open(resources, "rb") as f:
                    res = gff.read_gff(f.read())
                with open(os.path.join(WOTR, "RESOURCE.GFF"), "rb") as f:
                    sun = rp.emblem(SL, WOTR, gff.read_gff(f.read()))
                self.assertEqual((len(sun[0]), len(sun)), (32, 32))
                washed = rp._frame_rows(res[rp.EMPTY_FRAME], 1)
                self.assertEqual([r[rp.LEFT:rp.LEFT + rp.FACE] for r in washed[rp.TOP:rp.TOP + rp.FACE]], sun)
            self.assertNotIn(rp.SKIP, ravager.write_scripts(WOTR, scripts, {rp.SKIP}))
            self.assertNotIn(rp.SKIP, ravager.write_resources(WOTR, resources, {rp.SKIP}))


if __name__ == "__main__":
    unittest.main()
