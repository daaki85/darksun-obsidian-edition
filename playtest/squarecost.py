# squarecost.py LEGS COL1 ROW COL2 [POINTS]: what a walk costs in a fight, for the squares in reach: on a
# party member's turn it walks the member along row ROW between columns COL1 and COL2, LEGS times,
# its points set to POINTS (250) before each leg (a test's memory edit: never save after), and prints for
# each leg and in all the seconds walking, the map units a second and the frames shown a second
# (DSCLOG's flip_count, the header's +1832), then the frames a second standing still for 5 s. Run
# it with the marks on and off (the "squares" setting, the dice log started again) in turn.
import sys, os, struct, time, subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
legs, c1, row, c2 = (int(v) for v in sys.argv[1:5])
P = int(sys.argv[5]) if len(sys.argv) > 5 else 250
turn = gd.whose_turn(); cr = gd.combatant_creature(turn)
seg = (gd.load_seg + 0x37BD) * 16
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0xA0000, 0x100000, 16) if mem[i:i + 8] == b'DSCLOGve')


def pos():
    return struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + turn * 32, 4))


def flips():
    return struct.unpack('<H', g.read(hdr + 1832, 2))[0]


def arm():
    fl, = struct.unpack('<H', g.read(seg + 0x1D5 + cr * 2, 2))
    g.write(seg + 0x1D5 + cr * 2, struct.pack('<H', fl | 1))
    g.write(seg + 0x22B + cr * 2, struct.pack('<h', P))
    at = (gd.load_seg + 0x3972) * 16
    g.write(at + 0x377 + turn * 0x1C, b'\xff'); g.write(at + 0x8AA + turn * 0x13, b'\0\0')


def walk(col):
    cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
    arm()
    begun = pos()
    subprocess.run([sys.executable, os.path.join(PT, 'click.py'), str(col * 16 + 8 - cx), str(row * 16 + 8 - cy)],
                   stdout=subprocess.DEVNULL)
    t = time.monotonic()
    while pos() == begun and time.monotonic() - t < 4:
        time.sleep(0.005)
    t0, f0, last, still = time.monotonic(), flips(), pos(), time.monotonic()
    t1, f1 = t0, f0
    while time.monotonic() - t0 < 30:
        time.sleep(0.01)
        now = pos()
        if now != last:
            last, still = now, time.monotonic()
            t1, f1 = still, flips()
        elif time.monotonic() - still > 1.0:
            break
    return t1 - t0, abs(last[0] - begun[0]) + abs(last[1] - begun[1]), (f1 - f0) & 0xFFFF


walk(c1)
secs = units = frames = 0
for leg in range(legs):
    s, u, f = walk(c2 if leg % 2 == 0 else c1)
    print(f'leg {leg + 1}: {s:.2f} s, {u} units, {u / s:.1f} units/s, {f / s:.1f} frames/s', flush=True)
    secs += s; units += u; frames += f
print(f'walking: {units / secs:.1f} map units/s, {frames / secs:.1f} frames/s over {secs:.1f} s')
f0, t0 = flips(), time.monotonic(); time.sleep(5)
print(f'standing: {((flips() - f0) & 0xFFFF) / (time.monotonic() - t0):.1f} frames/s; squares_on {g.read(hdr + 1880, 1)[0]}')
