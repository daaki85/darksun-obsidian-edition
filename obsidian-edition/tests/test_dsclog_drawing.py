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
            with open(src, "w") as f:
                f.write(f"[map symbols {mp}]\n" + open(asm).read())
            subprocess.run(["nasm", "-f", "bin", "-I", os.path.dirname(asm) + "/", "-o", out, src], check=True)
            exe = open(out, "rb").read()
            sym = {}
            for line in open(mp).read().split("Section image")[1].splitlines():
                parts = line.split()
                if len(parts) == 3 and all(c in "0123456789ABCDEF" for c in parts[1]):
                    sym[parts[2]] = int(parts[1], 16)
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
        self.put("dark", bytes((c * 3 + 5) & 0xFF for c in range(256)))
        self.put("dark_ready", b"\x01")
        self.word("sc_seg", FAR)
        self.put("light", bytes(0 if c % 13 == 0 else (c + 2) & 0xFF for c in range(256)))
        self.put("red", bytes(0 if c % 17 == 0 else (c * 5 + 1) & 0xFF for c in range(256)))
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
        self.put("ring_tab", bytes(ring))
        puffs = bytearray()
        for n in range(10):
            sx, sy = spots[n]
            puffs += struct.pack("<HHHHHBx", CAM[0] + sx + 3, CAM[1] + sy + 2, TICK - (n * 2) % 19, things[n], (n * 0x3D7) & 0xFFFF, 1)
        self.put("puffs", bytes(puffs))

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
    out = []
    for args in CALLS:
        n = scene.floor(*args)
        out.append((scene.digest(), n))
    scene.out_of_memory(3)
    scene.out_of_memory(8)
    n = scene.floor(3, *CAM)
    out.append((scene.digest(), n))
    return out


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class FloorPassTests(unittest.TestCase):
    def test_built(self):
        """The helper as built from the source is DSCLOG.EXE (the symbols the tests use are its)."""
        self.assertEqual(build()[0], open(EXE, "rb").read(), "DSCLOG.EXE not rebuilt from dsclog.asm")

    def check(self, on, expected, most):
        got = floor_digests(on=on)
        for (digest, n), want, bound in zip(got, expected, most):
            print(f"  {digest} {n}", file=sys.stderr)
        self.assertEqual([d for d, _ in got], expected)
        for (digest, n), bound in zip(got, most):
            self.assertLessEqual(n, bound)
