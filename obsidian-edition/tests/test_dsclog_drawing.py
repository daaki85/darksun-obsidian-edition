"""DSCLOG's drawing on the map run in a CPU emulator (needs unicorn and nasm): the floor pass
(SHADOW_PASS: shadows, rings, dust), see-through figures (GHOST_DRAW) and the main loop's own
(DUST_TICK, PANEL_TICK), over a scene of figures, against a VGA whose four planes are emulated
(the map mask and read map set through the ports, as the helper sets them).

Each test checks the screen comes out as it did before the drawing code was made faster (the
SHA-256 of the planes after each call, taken from the build of 2026-11-08 before those changes),
and counts the instructions run (DOSBox charges about a cycle each), so a saving shows here as a
smaller count with the same picture.
"""

import hashlib
import os
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from unicorn import Uc, UC_ARCH_X86, UC_HOOK_CODE, UC_HOOK_INSN, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:  # optional dependency
    Uc = None

DOS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos")
ASM, EXE = os.path.join(DOS, "dsclog.asm"), os.path.join(DOS, "DSCLOG.EXE")
TSR, GAME_DS, SS, CALLER = 0x1000, 0x3000, 0x4000, 0x5000
FAR = 0xC000                    # (the far block, as the other tests put it)
LIST_SEG, PIC_SEG = 0x2000, 0x7000
CAM = (1000, 500)
HDR_SHADOWS_ON, HDR_DUST_ON, HDR_RINGS_ON, HDR_FAR_SEG, HDR_GHOST_SEG, HDR_GHOST_ON = 220, 234, 244, 142, 1826, 1828
HDR_RING_TAB, HDR_RED, HDR_LIGHT = 246, 248, 236  # (their offsets in the far block)
OBJ_LIST, OBJ_COUNT, MAP_THINGS, CACHE_LAST, CAM_X = 0x6690, 0x1F72, 0x6694, 0x1F84, 0x1178
LOAD = (GAME_DS - 0x4356) & 0xFFFF
CACHE = ((LOAD + 0x3E60) & 0xFFFF) * 16
PAGES = ((LOAD + 0x0980) & 0xFFFF) * 16
TICK = 1000                     # (the BIOS clock, 0:046Ch)

_built = {}


def build(asm=ASM):
    """The helper built from ASM with a symbol map: (its image, as loaded, and each symbol's offset)."""
    if asm not in _built:
        with tempfile.TemporaryDirectory() as tmp:
            src, out, mp = (os.path.join(tmp, n) for n in ("m.asm", "m.exe", "m.map"))
            with open(asm) as f:
                text = f.read()
            with open(src, "w") as f:
                f.write(f"[map symbols {mp}]\n" + text)
            subprocess.run(["nasm", "-f", "bin", "-I", os.path.dirname(asm) + "/", "-o", out, src], check=True)
            with open(out, "rb") as f:
                exe = f.read()
            with open(mp) as f:
                listing = f.read()
            sym = {}
            for line in listing.split("Section image")[1].split("---- Section")[0].splitlines():
                parts = line.split()
                if len(parts) == 3 and all(c in "0123456789ABCDEF" for c in parts[1]):
                    sym[parts[2]] = int(parts[1], 16)
            for line in listing.split("No Section")[1].split("---- Section")[0].splitlines():
                parts = line.split()  # (the EQUs: the far block's offsets, FAR_*)
                if len(parts) == 2 and parts[1].startswith("FAR_") and all(c in "0123456789ABCDEF" for c in parts[0]):
                    sym[parts[1]] = int(parts[0], 16)
        _built[asm] = (exe, sym)
    return _built[asm]


def frame_bytes(rng, w, h, ghost=False):
    """A frame of the game's pictures: width, height, then rows (its number, then runs: x with 8000h
    on the row's last, pixels, the data's length, the data: control bytes, REP numbers for GHOST)."""
    out = bytearray(struct.pack("<HH", w, h))
    for y in range(h):
        if rng.random() < 0.15:
            continue
        x, runs = rng.randrange(0, 6), []
        while x < w - 1 and len(runs) < 3:
            n = rng.randrange(1, min(12, w - x) + 1)
            runs.append((x, n))
            x += n + rng.randrange(1, 8)
        if not runs:
            continue
        out.append(y)
        for i, (x, n) in enumerate(runs):
            data = bytearray()
            left = n
            while left:
                k = rng.randrange(1, left + 1)
                if rng.random() < 0.4:
                    data += bytes((((k - 1) << 1) | 1, rng.randrange(32 if ghost else 256)))
                else:
                    data += bytes(((k - 1) << 1,)) + bytes(rng.randrange(32 if ghost else 256) for _ in range(k))
                left -= k
            out += struct.pack("<HBB", x | (0x8000 if i == len(runs) - 1 else 0), n, len(data)) + data
    out.append(0xFF)
    return bytes(out)


def floor(x, y):
    return (x * 7 + y * 13 + (x * y >> 5)) & 0xFF


class Scene:
    """The helper loaded, a page of the whole screen at A000h (page 3), and a VGA of four planes."""

    def __init__(self, asm=ASM):
        exe, self.sym = build(asm)
        image = bytearray(exe[struct.unpack_from("<H", exe, 8)[0] * 16:])
        for at in (HDR_FAR_SEG, 138, 268):
            image[at:at + 2] = struct.pack("<H", FAR)
        image[1834:1836] = struct.pack("<H", TSR + struct.unpack_from("<H", image, 1836)[0])  # (TAIL_SEG)
        self.image = image
        self.mu = mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, bytes(image))
        self.planes = [bytearray(0x10000) for _ in range(4)]
        self.mask, self.readmap, self.seq, self.gc = 15, 0, 0, 0
        self.count = 0
        mu.hook_add(UC_HOOK_INSN, self._out, None, 1, 0, r.UC_X86_INS_OUT)
        mu.hook_add(UC_HOOK_INSN, lambda uc, port, size, _: 0, None, 1, 0, r.UC_X86_INS_IN)
        mu.hook_add(UC_HOOK_MEM_READ, self._read, begin=0xA0000, end=0xAFFFF)
        mu.hook_add(UC_HOOK_MEM_WRITE, self._write, begin=0xA0000, end=0xAFFFF)
        mu.hook_add(UC_HOOK_CODE, self._counted, begin=TSR * 16, end=TSR * 16 + 0xFFFF)
        for field, value in ((4, 0xA000), (0x404, 0), (0x604, 0), (0x804, 319), (0xA04, 199), (0xC04, 0)):
            mu.mem_write(PAGES + 6 + field, struct.pack("<H", value))
        mu.mem_write(0x46C, struct.pack("<H", TICK))

    # the VGA
    def _byte_out(self, port, v):
        if port == 0x3C4:
            self.seq = v
        elif port == 0x3C5 and self.seq == 2:
            self.mask = v & 15
        elif port == 0x3CE:
            self.gc = v
        elif port == 0x3CF and self.gc == 4:
            self.readmap = v & 3

    def _out(self, uc, port, size, value, _):
        self._byte_out(port, value & 0xFF)
        if size == 2:
            self._byte_out(port + 1, value >> 8)

    def _read(self, uc, access, address, size, value, _):
        off = address - 0xA0000
        uc.mem_write(address, bytes(self.planes[self.readmap][off:off + size]))

    def _write(self, uc, access, address, size, value, _):
        off = address - 0xA0000
        data = (value & ((1 << 8 * size) - 1)).to_bytes(size, "little")
        for p in range(4):
            if self.mask >> p & 1:
                self.planes[p][off:off + size] = data

    def _counted(self, uc, address, size, _):
        self.count += 1

    def fill(self):
        for p in range(4):
            self.planes[p][:16000] = bytes(floor(b * 4 + p, y) for y in range(200) for b in range(80))

    def screen(self):
        return bytes(self.planes[x & 3][y * 80 + (x >> 2)] for y in range(200) for x in range(320))

    def digest(self):
        return hashlib.sha256(self.screen()).hexdigest()[:16]

    # memory
    def put(self, name, data, extra=0):
        self.mu.mem_write(TSR * 16 + self.sym[name] + extra, data)

    def put_far(self, field, data):
        """DATA at the far block's offset the header's FIELD holds (RING_TAB's, RED's)."""
        hdr = self.sym["hdr"]
        off, = struct.unpack_from("<H", self.image, hdr + field)
        self.mu.mem_write(FAR * 16 + off, data)

    def put_at_far(self, name, data):
        """DATA at the far block's NAME (an offset there: FAR_DARK, FAR_PUFFS...)."""
        self.mu.mem_write(FAR * 16 + self.sym[name], data)

    def get_at_far(self, name, n):
        return bytes(self.mu.mem_read(FAR * 16 + self.sym[name], n))

    def get(self, name, n, extra=0):
        return bytes(self.mu.mem_read(TSR * 16 + self.sym[name] + extra, n))

    def word(self, name, value, extra=0):
        self.put(name, struct.pack("<H", value & 0xFFFF), extra)

    def ds(self, at, data):
        self.mu.mem_write(GAME_DS * 16 + at, data)

    def run(self, at, until, sp, **regs):
        """From the helper's AT to CALLER:UNTIL; the instructions run."""
        mu = self.mu
        for name, value in dict(dict(cs=TSR, ds=GAME_DS, es=GAME_DS, ss=SS, esp=sp, ebp=0x1000), **regs).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.count = 0
        mu.emu_start(TSR * 16 + at, CALLER * 16 + until, count=20_000_000)
        self.assertion(mu.reg_read(r.UC_X86_REG_CS) * 16 + mu.reg_read(r.UC_X86_REG_IP) == CALLER * 16 + until)
        return self.count

    def call(self, name, **regs):
        """The helper's routine NAME, a near call; the instructions run."""
        sp = 0x7F0
        self.mu.mem_write(SS * 16 + sp, struct.pack("<H", 0xFFF0))
        for name_, value in dict(dict(cs=TSR, ds=GAME_DS, es=GAME_DS, ss=SS, esp=sp), **regs).items():
            self.mu.reg_write(getattr(r, "UC_X86_REG_" + name_.upper()), value)
        self.count = 0
        self.mu.emu_start(TSR * 16 + self.sym[name], TSR * 16 + 0xFFF0, count=1_000_000)
        self.assertion(self.mu.reg_read(r.UC_X86_REG_IP) == 0xFFF0)
        return self.count

    @staticmethod
    def assertion(ok):
        if not ok:
            raise AssertionError("the routine didn't come back")


class Figures(Scene):
    """A scene of figures on the map: 14 cast shadows (some mirrored, two on fixed places, one under
    a ring, one under the chosen enemy's), 46 other things in the list, 10 puffs of dust."""
    CASTERS = 14

    def __init__(self, asm=ASM, on=(1, 1, 1)):
        super().__init__(asm)
        rng = random.Random(7)
        mu = self.mu
        shadows, dust, rings = on
        hdr = self.sym["hdr"]
        mu.mem_write(TSR * 16 + hdr + HDR_SHADOWS_ON, struct.pack("<H", shadows))
        mu.mem_write(TSR * 16 + hdr + HDR_DUST_ON, struct.pack("<H", dust))
        mu.mem_write(TSR * 16 + hdr + HDR_RINGS_ON, struct.pack("<H", rings))
        self.put_at_far("FAR_DARK", bytes((c * 3 + 5) & 0xFF for c in range(256)))
        self.put("dark_ready", b"\x01")
        self.word("sc_seg", FAR)
        self.put_far(HDR_LIGHT, bytes(0 if c % 13 == 0 else (c + 2) & 0xFF for c in range(256)))
        self.put_far(HDR_RED, bytes(0 if c % 17 == 0 else (c * 5 + 1) & 0xFF for c in range(256)))
        things = rng.sample(range(520), 60)
        self.things = things
        self.ds(OBJ_LIST, struct.pack("<HH", 0, LIST_SEG))
        self.ds(OBJ_COUNT, struct.pack("<H", 60))
        self.ds(CACHE_LAST, struct.pack("<H", 40))
        self.ds(CAM_X, struct.pack("<HH", *CAM))
        tab = bytearray(65)
        pic = PIC_SEG
        spots = [(-30, 20), (10, 150), (60, 60), (100, 110), (150, 30), (190, 170), (230, 90), (270, 140),
                 (300, 60), (310, 185), (120, 196), (-90, 60), (500, 80), (200, 260)]
        for n, thing in enumerate(things):
            sx, sy = spots[n] if n < self.CASTERS else (rng.randrange(-100, 420), rng.randrange(-60, 260))
            mirrored = n % 3 == 1
            fixed = n in (4, 9)
            w, h = rng.randrange(20, 48), rng.randrange(40, 80)
            x, y = CAM[0] + sx, CAM[1] + sy
            mu.mem_write(LIST_SEG * 16 + n * 8, struct.pack("<HHBBH", x, y, 0, (0x80 if mirrored else 0) | (0 if fixed else 0x20), thing))
            slot = n + 1
            rec = bytearray(32)
            rec[7], rec[8] = w // 2, h - 4
            struct.pack_into("<HH", rec, 3, x - w // 2, y - h + 4)
            struct.pack_into("<H", rec, 0x0F, slot)
            rec[0x11] = n & 1
            self.ds(MAP_THINGS + thing * 32, bytes(rec))
            frames = [frame_bytes(rng, w, h), frame_bytes(rng, w, h)]
            body = struct.pack("<HHH", 0, 0, 2) + struct.pack("<II", 14, 14 + len(frames[0])) + frames[0] + frames[1]
            mu.mem_write(pic * 16, body)
            mu.mem_write(CACHE + slot * 16, struct.pack("<6xIHHH", 5000 + n, 0, pic, 2))
            pic += (len(body) + 15) // 16
            if n < self.CASTERS:
                tab[thing // 8] |= 1 << thing % 8
        self.put("shadow_tab", bytes(tab))
        ring = bytearray(520)
        ring[things[2]], ring[things[6]] = 1, 2
        self.put_far(HDR_RING_TAB, bytes(ring))
        puffs = bytearray()
        for n in range(10):
            sx, sy = spots[n]
            puffs += struct.pack("<HHHHHBx", CAM[0] + sx + 3, CAM[1] + sy + 2, TICK - (n * 2) % 19, things[n], (n * 0x3D7) & 0xFFFF, 1)
        self.put_at_far("FAR_PUFFS", bytes(puffs))

    def out_of_memory(self, n):
        """Thing N's picture let go of by the cache (its shadow from the shadows' cache, SC_SEG)."""
        self.mu.mem_write(CACHE + (n + 1) * 16 + 0x0E, b"\x00")

    def floor(self, *args):
        """FLOOR_POST after the game's floor routine: the whole view's (page, camera x, y) or a
        rectangle's (page, x0, y0, x1 + 1, y1, camera x, y); the floor put back first."""
        self.fill()
        self.put("floor_kind", bytes((int(len(args) > 3),)))
        self.put("floor_ret", struct.pack("<HH", 0x700, CALLER))
        sp = 0x800 - 2 * len(args)
        self.mu.mem_write(SS * 16 + sp, struct.pack(f"<{len(args)}H", *args))
        return self.run(self.sym["floor_post"], 0x700, sp)


# the floor calls of a frame drawn round the combat log's panel (REDRAW_PARTS: above it, to its left,
# the strip to its right, and the rows below), a small rectangle, and the whole view
CALLS = [(3, 0, 0, 320, 119) + CAM, (3, 0, 120, 136, 199) + CAM, (3, 316, 120, 320, 199) + CAM,
         (3, 180, 40, 260, 100) + CAM, (3, 0, 196, 320, 199) + CAM, (3,) + CAM]


def floor_digests(asm=ASM, on=(1, 1, 1)):
    """Each call's screen and instructions; then the whole view again with one picture let go of."""
    scene = Figures(asm, on)
    if on[1] and "dust_build" in scene.sym:  # (its table made once, as the first pass would: not counted)
        scene.call("dust_build")
    out = []
    for args in CALLS:
        n = scene.floor(*args)
        out.append((scene.digest(), n))
    scene.out_of_memory(3)
    scene.out_of_memory(8)
    n = scene.floor(3, *CAM)
    out.append((scene.digest(), n))
    return out


GHOST_SEG = 0x8800
GH_REP, GH_TAB = 32 * 256, 32 * 256 + 256


class Ghosts(Scene):
    """See-through figures (GHOST_DRAW): BLEND and REP made up, pictures of REP numbers."""

    def __init__(self, asm=ASM):
        super().__init__(asm)
        rng = random.Random(11)
        mu = self.mu
        hdr = self.sym["hdr"]
        mu.mem_write(TSR * 16 + hdr + HDR_GHOST_SEG, struct.pack("<H", GHOST_SEG))
        mu.mem_write(TSR * 16 + hdr + HDR_GHOST_ON, struct.pack("<H", 1))
        mu.mem_write(GHOST_SEG * 16, bytes((rep * 37 + under * 3 + 1) & 0xFF for rep in range(32) for under in range(256)))
        mu.mem_write(GHOST_SEG * 16 + GH_REP, bytes(rng.randrange(32) for _ in range(256)))
        self.pictures = []
        pic = PIC_SEG
        for n in range(4):
            w, h = rng.randrange(24, 60), rng.randrange(40, 90)
            frames = [frame_bytes(rng, w, h, ghost=True), frame_bytes(rng, w, h, ghost=True)]
            body = struct.pack("<HHH", 0, 0, 2) + struct.pack("<II", 14, 14 + len(frames[0])) + frames[0] + frames[1]
            mu.mem_write(pic * 16, body)
            self.pictures.append(pic)
            pic += (len(body) + 15) // 16

    def draw(self, x, y, mirrored, picture, frame):
        """GHOST_DRAW (a near call: page 3, X, Y, MIRRORED, the picture, FRAME)."""
        sp = 0x800 - 16
        self.mu.mem_write(SS * 16 + sp, struct.pack("<HHhhHHHH", 0xFFF0, 3, x, y, mirrored, 0, self.pictures[picture], frame))
        mu = self.mu
        for name, value in dict(cs=TSR, ds=GAME_DS, es=GAME_DS, ss=SS, esp=sp, ebp=0x1000).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        self.count = 0
        mu.emu_start(TSR * 16 + self.sym["ghost_draw"], TSR * 16 + 0xFFF0, count=20_000_000)
        self.assertion(mu.reg_read(r.UC_X86_REG_IP) == 0xFFF0 and mu.reg_read(r.UC_X86_REG_SP) == sp + 2)
        return self.count


GHOST_CALLS = [(100, 40, 0, 0, 0), (200, 60, 1, 1, 1), (-20, 150, 0, 2, 1), (290, -30, 1, 3, 0), (150, 120, 0, 1, 0)]


def ghost_digests(asm=ASM):
    scene = Ghosts(asm)
    scene.fill()
    out = []
    for args in GHOST_CALLS:
        n = scene.draw(*args)
        out.append((scene.digest(), n))
    return out


# The screens as drawn before the drawing code was made faster (2026-11-08), and the instructions
# that took then; for each of FLOOR_CALLS' calls (and the whole view again, two pictures let go
# of), with shadows, dust and rings on, then each alone.
BEFORE = {
    (1, 1, 1): [("6aa66587bcd7f8c1", 149207), ("4fb5147fe7341df2", 52500), ("720c255ac21d0459", 44346),
                ("aadbffb618ae5c5e", 58941), ("3385041c16e9bd1a", 47153), ("7a3c3f67e2365e15", 190508),
                ("2436812d5be1b5dd", 184435)],
    (1, 0, 0): [("b117771caf8c0526", 99563), ("2f7ed1a7a5520fe9", 44596), ("720c255ac21d0459", 38099),
                ("a25593731c3651be", 33073), ("3385041c16e9bd1a", 40834), ("c9bf888a6d0af4e8", 126962),
                ("f85be6ebe12a850c", 120889)],
    (0, 1, 0): [("82ec5702100be2cc", 24832), ("63a3f73e36d4513d", 2378), ("8dae532d8049c840", 721),
                ("05d08337bdc14edc", 7355), ("8dae532d8049c840", 792), ("4a2750adb53fd1b8", 38721),
                ("4a2750adb53fd1b8", 38721)],
    (0, 0, 1): [("1ed71773a3ac3e89", 25183), ("8dae532d8049c840", 5912), ("8dae532d8049c840", 5912),
                ("e8aca136d6f189c3", 18902), ("8dae532d8049c840", 5911), ("1ed71773a3ac3e89", 25170),
                ("1ed71773a3ac3e89", 25170)],
}
GHOST_BEFORE = [("fc41731b1d04863d", 44419), ("816d835642c05749", 34653), ("9416c1412df146d2", 15491),
                ("a22720eab61cbd3c", 37258), ("225f0bf11bdf482e", 36336)]


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class DrawingTests(unittest.TestCase):
    def test_built(self):
        """The helper as built from the source is DSCLOG.EXE (the symbols these tests use are its)."""
        with open(EXE, "rb") as f:
            self.assertEqual(build()[0], f.read(), "DSCLOG.EXE not rebuilt from dsclog.asm")

    def same_and_fewer(self, got, before, saved):
        """The same screens as BEFORE; all the calls together at least SAVED (a fraction) cheaper."""
        self.assertEqual([d for d, _ in got], [d for d, _ in before])
        now, then = sum(n for _, n in got), sum(n for _, n in before)
        print(f"  {then} -> {now} instructions ({100 * (then - now) / then:.0f}% fewer)", file=sys.stderr)
        self.assertLessEqual(now, then * (1 - saved))

    def test_floor_pass(self):
        """SHADOW_PASS's screens as before, in fewer instructions: the shadows' (a figure's shadow
        tested against the clip from its frame's size, rows outside it passed over, the slot it was
        kept in remembered, the spans a plane at a time through XLAT), the dust's (its thickness
        from DUST_BUILD's table), the rings' (the list's things not marked passed over sooner)."""
        for on, saved in (((1, 1, 1), 0.25), ((1, 0, 0), 0.35), ((0, 1, 0), 0.15), ((0, 0, 1), 0.01)):
            with self.subTest(on=on):
                self.same_and_fewer(floor_digests(on=on), BEFORE[on], saved)

    def test_ghost_draw(self):
        """GHOST_DRAW's see-through figures as before (mirrored, clipped at the page's edges), each
        pixel's REP number through XLAT in place of a call."""
        self.same_and_fewer(ghost_digests(), GHOST_BEFORE, 0.08)

    def test_dark_retried_twice_a_second(self):
        """A palette too dark for DARK (a fade, or a dark area) is tried again every DARK_RETRY
        ticks of the BIOS clock, not in every floor pass (768 port reads and the sums each time)."""
        scene = Figures()
        hdr = scene.sym["hdr"]
        mu = scene.mu
        tried = []
        at = TSR * 16 + scene.sym["build_dark"]
        mu.hook_add(UC_HOOK_CODE, lambda *a: tried.append(1), begin=at, end=at)
        for tick, expected in ((TICK, 1), (TICK, 1), (TICK + 3, 1), (TICK + 9, 2), (TICK + 10, 2)):
            mu.mem_write(TSR * 16 + hdr + 224, struct.pack("<H", 1))  # (the Loader's DARK_BUILD)
            mu.mem_write(0x46C, struct.pack("<H", tick))
            scene.floor(3, *CAM)
            self.assertEqual(len(tried), expected)
            self.assertEqual(struct.unpack("<H", mu.mem_read(TSR * 16 + hdr + 224, 2))[0], 1)  # (still asked)

    def test_floor_rect_marks_the_panel(self):
        """FLOOR_ENTER marks the combat log's panel to be put again only when the floor drawn
        reaches it (or is the whole view): REDRAW_PARTS' rectangles round it don't."""
        scene = Scene()
        sym, mu = scene.sym, scene.mu
        scene.word("panel_on", 1)
        scene.word("panel_top", 120)
        scene.word("panel_rows", 78)

        def enter(probe, args):
            scene.put("panel_dirty", b"\x00")
            sp = 0x800 - 2 * len(args) - 4 - 6
            mu.mem_write(SS * 16 + sp, struct.pack("<3H", 0x602, CALLER, 0x0202) + struct.pack("<2H", 0x700, CALLER)
                         + struct.pack(f"<{len(args)}h", *args))
            scene.run(sym[probe], 0x602, sp)
            return scene.get("panel_dirty", 1)[0]
        cam = CAM
        self.assertEqual(enter("probe_floor_all", (3,) + cam), 1)
        for rect, dirty in (((0, 0, 320, 119), 0), ((0, 120, 136, 199), 0), ((316, 120, 320, 199), 0),
                            ((0, 0, 320, 120), 1), ((132, 150, 140, 160), 1), ((312, 190, 316, 199), 1),
                            ((136, 198, 200, 199), 0)):
            with self.subTest(rect=rect):
                self.assertEqual(enter("probe_floor_rect", (3,) + rect + cam), dirty)

    def test_rings_alone_widen_less(self):
        """With rings on and shadows off, the rectangle the game draws again round what moved
        reaches only as far as a ring does (RING_RIGHT, RING_DOWN), not as far as a shadow."""
        scene = Scene()
        mu, sym, hdr = scene.mu, scene.sym, scene.sym["hdr"]
        bp = 0x1000

        def widened(shadows, rings):
            mu.mem_write(TSR * 16 + hdr + HDR_SHADOWS_ON, struct.pack("<H", shadows))
            mu.mem_write(TSR * 16 + hdr + HDR_RINGS_ON, struct.pack("<H", rings))
            mu.mem_write(SS * 16 + bp - 0x0E, struct.pack("<4H", 100, 60, 151, 40))  # y1, y0, x1, x0
            mu.mem_write(SS * 16 + bp + 6, struct.pack("<5H", 0, 0, 0, 0, 0))
            sp = bp - 0x20 - 6
            mu.mem_write(SS * 16 + sp, struct.pack("<3H", 0x602, CALLER, 0x0202))
            scene.run(sym["probe_redraw_all"], 0x602, sp, ebp=bp)
            y1, y0, x1, x0 = struct.unpack("<4H", mu.mem_read(SS * 16 + bp - 0x0E, 8))
            return x1 - 151, y1 - 100
        self.assertEqual(widened(0, 0), (0, 0))
        self.assertEqual(widened(1, 0), (72, 44))
        self.assertEqual(widened(1, 1), (72, 44))
        self.assertEqual(widened(0, 1), (16, 8))

    def test_view_drawn_again_once_a_pass(self):
        """VIEW_AGAIN draws the view again once in a pass of the main loop (the panel's and the
        labels' both asked for it when the view scrolled), and again in the next pass."""
        scene = Scene()
        mu, sym = scene.mu, scene.sym
        centre = ((GAME_DS - 0x4356 + 0x191F) & 0xFFFF) * 16 + 0x0281
        mu.mem_write(centre, b"\xcb")  # retf
        calls = []
        mu.hook_add(UC_HOOK_CODE, lambda *a: calls.append(1), begin=centre, end=centre)
        stop = CALLER * 16 + 0x700
        mu.mem_write(stop - 3, b"\xe8" + struct.pack("<h", 0))

        def again():
            sp = 0x7F0
            mu.mem_write(SS * 16 + sp, struct.pack("<H", 0xFFF0))
            for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=sp).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.emu_start(TSR * 16 + sym["view_again"], TSR * 16 + 0xFFF0, count=1000)
        scene.put("va_done", b"\x00")
        again()
        again()
        self.assertEqual(len(calls), 1)
        scene.put("va_done", b"\x00")  # (PROBE_SCROLL's next pass)
        again()
        self.assertEqual(len(calls), 2)

    def test_dust_a_puff_every_six_pixels(self):
        """DUST_TICK raises a puff behind a walker every DUST_STEP pixels it walks (it took the
        BIOS clock's low byte for the distance, so a puff nearly every pass), and none behind one
        walking off the view."""
        scene = Scene()
        mu, sym, hdr = scene.mu, scene.sym, scene.sym["hdr"]
        mu.mem_write(TSR * 16 + hdr + HDR_DUST_ON, struct.pack("<H", 1))
        tab = bytearray(65)
        for thing in (5, 9):
            tab[thing // 8] |= 1 << thing % 8
        scene.put("shadow_tab", bytes(tab))
        scene.ds(OBJ_LIST, struct.pack("<HH", 0, LIST_SEG))
        scene.ds(OBJ_COUNT, struct.pack("<H", 2))
        scene.ds(CAM_X, struct.pack("<HH", *CAM))

        def puffs():
            return struct.unpack("<H", mu.mem_read(TSR * 16 + hdr + 240, 2))[0]
        for step in range(31):  # (thing 5 on the view, thing 9 far off it, each 2 pixels a pass)
            x = CAM[0] + 100 + 2 * step
            mu.mem_write(LIST_SEG * 16, struct.pack("<HHBBH", x, CAM[1] + 100, 0, 0x20, 5)
                         + struct.pack("<HHBBH", x + 900, CAM[1] + 100, 0, 0x20, 9))
            mu.mem_write(0x46C, struct.pack("<H", TICK + step))
            sp = 0x7F0
            mu.mem_write(SS * 16 + sp, struct.pack("<H", 0xFFF0))
            for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=sp).items():
                mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
            mu.emu_start(TSR * 16 + sym["dust_tick"], TSR * 16 + 0xFFF0, count=100000)
            if step == 0:
                self.assertEqual(puffs(), 0)  # (the first pass: where each is noted, a jump)
        self.assertEqual(puffs(), 10)  # (60 pixels walked)
        owners = {struct.unpack_from("<H", scene.get_at_far("FAR_PUFFS", 24 * 12), n * 12 + 6)[0] for n in range(10)}
        self.assertEqual(owners, {5})

    def test_no_labels_nothing_done(self):
        """LABEL_STAMP (from the timer, about 60 times a second) does next to nothing when no slot
        holds a label: no reads of the CRTC, no VGA registers kept and put back."""
        scene = Scene()
        mu, sym = scene.mu, scene.sym
        scene.put("pointer_ds", struct.pack("<H", GAME_DS))
        scene.ds(0x0BC9, struct.pack("<H", 1))  # (on the map)
        sp = 0x7F0
        mu.mem_write(SS * 16 + sp, struct.pack("<H", 0xFFF0))
        for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=sp).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        scene.count = 0
        mu.emu_start(TSR * 16 + sym["label_stamp"], TSR * 16 + 0xFFF0, count=10000)
        self.assertLess(scene.count, 15)
