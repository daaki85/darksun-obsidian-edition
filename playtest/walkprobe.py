# walkprobe.py N X Y DIR [SECS]: a click at screen X, Y (game pixels), then for SECS seconds (default 6)
# as often as it can: party member N's map position, whose turn it is (the game's word), DSCLOG's
# STEALTH word (header +204: bit N set while N is hidden, so drawn see-through) and a window grab
# (DIR/pNNN.png, 320x240). Prints one line a sample: the time from the click, the grab, the position,
# the turn and STEALTH, so each frame can be set against the turn passing.
# Made 2026-11-06 for the solid-frames question (logs/2026-11-06-solid-frames-turn-end.md).
import os, sys, struct, time, subprocess
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game
n, X, Y = map(int, sys.argv[1:4]); out = sys.argv[4]
secs = float(sys.argv[5]) if len(sys.argv) > 5 else 6.0
os.makedirs(out, exist_ok=True)
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0, len(mem), 16) if mem[i:i + 8] == b'DSCLOGva')
def sample():
    x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + n * 32, 4))
    st = struct.unpack('<H', g.read(hdr + 204, 2))[0]
    return (x, y), gd.whose_turn(), st
wid = subprocess.run(['xdotool', 'search', '--class', 'dosbox'], capture_output=True, text=True).stdout.split()[0]
print('before', *sample())
subprocess.run(['python3', os.path.join(PT, 'click.py'), str(X), str(Y), 'left'], capture_output=True)
t0 = time.time(); k = 0
while time.time() - t0 < secs and k < 400:
    s = sample()
    f = f'{out}/p{k:03d}.png'
    subprocess.run(['import', '-window', wid, f])
    print('%.2f' % (time.time() - t0), os.path.basename(f), *s, flush=True); k += 1
