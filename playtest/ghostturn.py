# ghostturn.py: in a fight, GHOST_UNION's whole view on a GHOST_TAB change (GH_CHANGED) in the
# enemies' turns: at the start of one enemy turn Cermak (thing 2) is marked see-through without the
# changed byte (the control), at the next one with it; window grabs every 0.1 s through each enemy
# turn ($WORK/ctrl_N.png, with_N.png); the party's turns passed through the END menu. The table is put
# back clear (with the byte) at the end. Memory only.
import os, sys, struct, subprocess, time; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0, len(mem), 16) if mem[i:i + 8] == b'DSCLOGva')
seg = struct.unpack('<H', g.read(hdr + 1826, 2))[0]
TAB = seg * 16 + 8192 + 256
def mark(thing, changed):
    bits = bytearray(65)
    if thing is not None: bits[thing // 8] |= 1 << thing % 8
    g.write(TAB, bytes(bits)); g.write(TAB + 79, bytes((changed,)))
def turn(): return gd.whose_turn()
def grab(name):
    win = subprocess.run(['xdotool', 'search', '--class', 'dosbox'], capture_output=True, text=True).stdout.split()[0]
    subprocess.run(['import', '-window', win, name], capture_output=True)
def pass_party(t):
    cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
    x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + t * 32, 4))
    sx, sy = x - cx, y - cy - 12
    if 5 < sx < 315 and 20 < sy < 190:
        subprocess.run([sys.executable, os.path.join(HERE, 'click.py'), str(sx), str(sy)], capture_output=True, timeout=10)
        time.sleep(0.9); subprocess.run(['xdotool', 'key', 'e']); time.sleep(1.2)
    cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
    if (cx, cy) == (0, 0):
        subprocess.run(['xdotool', 'key', 'Escape']); time.sleep(1)
        subprocess.run([sys.executable, os.path.join(HERE, 'viewto.py'), '1912', '872'], capture_output=True, timeout=120)
phases = [('ctrl', 0), ('with', 1)]
t0 = time.time()
while phases and time.time() - t0 < 600:
    if not gd.fight_on(): print('fight over'); break
    t = turn()
    if t is not None and t <= 3:
        pass_party(t); continue
    name, changed = phases.pop(0)
    mark(2, changed); print(name, 'marked at enemy turn', t, flush=True)
    n = 0
    while turn() is not None and turn() > 3 and n < 80:
        n += 1; grab(os.path.join(WORK, '%s_%02d.png' % (name, n))); time.sleep(0.1)
    print(name, n, 'grabs; changed byte now', g.read(TAB + 79, 1).hex(), 'turn', turn(), flush=True)
    mark(None, 1)
    while turn() is not None and turn() > 3: time.sleep(0.05)
print('done')
