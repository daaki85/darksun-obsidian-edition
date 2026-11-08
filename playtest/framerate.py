# framerate.py SECONDS [X1 X2 Y]: walks the party back and forth between screen points (X1,Y) and
# (X2,Y) for SECONDS and reports, a second at a time and in all: the map's main loop passes
# (DSCLOG's main_ticks, header +260), the frames shown (flip_count, +1832) and those steady pace left
# undrawn (pace_skipped: found with a symbol map of the helper as built), the BIOS
# clock against the wall clock (18.2 a second when DOSBox keeps real time), the leader's map units
# walked a second while walking (the time waiting at a target left out), the game's clock (96 ticks a
# second) and, with steady pace on, its steps run and lost (a tick of the clock that passed while a
# frame was drawn: a step each walker doesn't take), and DOSBox's CPU use. Out of a fight.
import os, sys, struct, time, subprocess
PLAYTEST = os.path.dirname(os.path.abspath(__file__))
secs = float(sys.argv[1]); x1, x2, y = (int(v) for v in (sys.argv[2:5] if len(sys.argv) > 4 else (40, 280, 104)))
sys.argv = sys.argv[:1]
sys.path.insert(0, PLAYTEST); __file__ = os.path.join(PLAYTEST, "live.py"); exec(open(__file__).read())
def symbols(*names):  # (their offsets from the header, from a symbol map of the helper as built)
    import tempfile
    dos = os.path.join(os.path.dirname(PLAYTEST), "obsidian-edition", "dos")
    with tempfile.TemporaryDirectory() as tmp:
        src, out, mp = (os.path.join(tmp, n) for n in ("m.asm", "m.bin", "m.map"))
        asm = os.environ.get("DSCLOG_ASM", os.path.join(dos, "dsclog.asm"))  # (another build's source, for its EXE)
        open(src, "w").write(f"[map symbols {mp}]\n" + open(asm).read())
        subprocess.run(["nasm", "-f", "bin", "-I", dos + "/", "-o", out, src], check=True)
        found = {}
        for line in open(mp).read().split("Section image")[1].splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[2] in names:
                found[parts[2]] = int(parts[1], 16)
    missing = [n for n in names if n not in found]
    if missing:
        raise SystemExit(f"no {missing}")
    return [found[n] for n in names]
SKIPPED, FLIPS, RAN, LOST = symbols("pace_skipped", "flip_count", "pace_ran", "pace_lost")
hdr = None
for at in range(0xC0000, 0xF0000, 16):
    if g.read(at, 8) == b"DSCLOGva":
        hdr = at; break
assert hdr, "no DSCLOG header"
def snap():
    ticks, = struct.unpack("<H", g.read(hdr + 260, 2))
    skipped, = struct.unpack("<H", g.read(hdr + SKIPPED, 2))
    bios, = struct.unpack("<I", g.read(0x46C, 4))
    flips, = struct.unpack("<H", g.read(hdr + FLIPS, 2))
    x, yy = struct.unpack("<hh", g.read(ds * 16 + 0x669D, 4))
    ran, lost = struct.unpack("<H", g.read(hdr + RAN, 2))[0], struct.unpack("<H", g.read(hdr + LOST, 2))[0]
    clock, = struct.unpack("<I", g.read(ds * 16 + 0x11D6, 4))
    return time.monotonic(), ticks, skipped, bios, x, yy, flips, ran, lost, clock
pid = subprocess.run(["pgrep", "-x", "dosbox"], capture_output=True, text=True).stdout.split()[0]
cpu0 = sum(int(v) for v in open(f"/proc/{pid}/stat").read().split()[13:15])
first = last = snap(); walked = 0; moving = 0.0; target = 0; next_click = 0.0
while time.monotonic() - first[0] < secs:
    now = time.monotonic()
    if now >= next_click:
        subprocess.run(["python3", os.path.join(PLAYTEST, "click.py"), str((x1, x2)[target]), str(y)], capture_output=True)
        target ^= 1; next_click = time.monotonic() + 3.0
    time.sleep(0.25)
    s = snap()
    step = abs(s[4] - last[4]) + abs(s[5] - last[5])
    if step:  # (the leader's speed while walking: the time waiting at a target left out)
        walked += step; moving += s[0] - last[0]
    last = s
end = snap()
cpu1 = sum(int(v) for v in open(f"/proc/{pid}/stat").read().split()[13:15])
dt = end[0] - first[0]
d = lambda i: (end[i] - first[i]) % 65536
passes, skipped = d(1), d(2)
print(f"{dt:.1f} s: frames shown {d(6) / dt:.1f}/s, undrawn (steady pace) {skipped / dt:.1f}/s, main loop {passes / dt:.0f}/s; "
      f"BIOS clock {(end[3] - first[3]) / dt:.1f}/s (18.2 = real time); game clock {d(9) / dt:.0f}/s, "
      f"steps run {d(7) / dt:.0f}/s, lost while drawing {d(8) / dt:.0f}/s (steady pace on only); "
      f"walking {walked / max(moving, 0.01):.0f} map units/s; "
      f"DOSBox CPU {100 * (cpu1 - cpu0) / os.sysconf('SC_CLK_TCK') / dt:.0f}%")
