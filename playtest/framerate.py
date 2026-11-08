# framerate.py SECONDS [X1 X2 Y]: walks the party back and forth between screen points (X1,Y) and
# (X2,Y) for SECONDS and reports, a second at a time and in all: the map's main loop passes
# (DSCLOG's main_ticks, header +260), the frames shown (flip_count, +1832) and those steady pace left
# undrawn (pace_skipped: found with a symbol map of the helper as built), the BIOS
# clock against the wall clock (18.2 a second when DOSBox keeps real time), the leader's map units
# walked, and DOSBox's CPU use. Out of a fight.
import os, sys, struct, time, subprocess
PLAYTEST = os.path.dirname(os.path.abspath(__file__))
secs = float(sys.argv[1]); x1, x2, y = (int(v) for v in (sys.argv[2:5] if len(sys.argv) > 4 else (40, 280, 104)))
sys.argv = sys.argv[:1]
sys.path.insert(0, PLAYTEST); __file__ = os.path.join(PLAYTEST, "live.py"); exec(open(__file__).read())
def symbol(name):  # (its offset from the header, from a symbol map of the helper as built)
    import tempfile
    dos = os.path.join(os.path.dirname(PLAYTEST), "obsidian-edition", "dos")
    with tempfile.TemporaryDirectory() as tmp:
        src, out, mp = (os.path.join(tmp, n) for n in ("m.asm", "m.bin", "m.map"))
        open(src, "w").write(f"[map symbols {mp}]\n" + open(os.path.join(dos, "dsclog.asm")).read())
        subprocess.run(["nasm", "-f", "bin", "-I", dos + "/", "-o", out, src], check=True)
        for line in open(mp).read().split("Section image")[1].splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[2] == name:
                return int(parts[1], 16)
    raise SystemExit(f"no {name}")
SKIPPED, FLIPS = symbol("pace_skipped"), symbol("flip_count")
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
    return time.monotonic(), ticks, skipped, bios, x, yy, flips
pid = subprocess.run(["pgrep", "-x", "dosbox"], capture_output=True, text=True).stdout.split()[0]
cpu0 = sum(int(v) for v in open(f"/proc/{pid}/stat").read().split()[13:15])
first = last = snap(); walked = 0; target = 0; next_click = 0.0
while time.monotonic() - first[0] < secs:
    now = time.monotonic()
    if now >= next_click:
        subprocess.run(["python3", os.path.join(PLAYTEST, "click.py"), str((x1, x2)[target]), str(y)], capture_output=True)
        target ^= 1; next_click = time.monotonic() + 3.0
    time.sleep(0.25)
    s = snap()
    walked += abs(s[4] - last[4]) + abs(s[5] - last[5])
    last = s
end = snap()
cpu1 = sum(int(v) for v in open(f"/proc/{pid}/stat").read().split()[13:15])
dt = end[0] - first[0]
d = lambda i: (end[i] - first[i]) % 65536
passes, skipped = d(1), d(2)
print(f"{dt:.1f} s: frames shown {d(6) / dt:.1f}/s, undrawn (steady pace) {skipped / dt:.1f}/s, main loop {passes / dt:.0f}/s; "
      f"BIOS clock {(end[3] - first[3]) / dt:.1f}/s (18.2 = real time); walked {walked / dt:.0f} map units/s; "
      f"DOSBox CPU {100 * (cpu1 - cpu0) / os.sysconf('SC_CLK_TCK') / dt:.0f}%")
