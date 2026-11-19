# ravfight.py [state|end|wait N|cast SPELL_ICON_X SPELL_ICON_Y LEVELS] [PID]: Wake of the Ravager's fight by
# its memory. state: whose turn (DS:426Dh: 0-3 the party), the camera (DS:1408h) and each map object's
# place (the records 25h bytes apart from DS:67BBh, map x +3, y +5; on screen x - camera x, y -
# camera y, in game pixels; 0-3 the party; a figure's body about 12 right and 18 down of it). end: the
# member whose turn it is ends it (Q, the manual's key). wait N: until a party member's turn, at most N s.
# cast X Y LEVELS: USE, LEVEL pressed LEVELS times, the spell's icon at X,Y, then aimed at the nearest
# object that isn't the party's and pressed. Prints what it did. Run from playtest/.
import sys, os, time, struct, argparse, subprocess
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest'); os.environ.setdefault('DISPLAY', ':55')
pid = int(open(os.path.join(WORK, 'rav.pid')).read())
g = connect(argparse.Namespace(pid=pid, host_base=None)); ds = game.find_data_segment(g)
w = lambda off: struct.unpack('<H', g.read(ds*16 + off, 2))[0]
def turn(): return w(0x426D)
def objects():
    cx, cy = struct.unpack('<HH', g.read(ds*16 + 0x1408, 4)); out = []
    for i in range(32):
        r = g.read(ds*16 + 0x67BB + 0x25*i, 0x25)
        if r[:4] == b'\xff\xff\xff\xff' and r[4:8] == b'\xff\xff\xff\xff': continue
        x, y = struct.unpack_from('<HH', r, 3)
        if x < 0x8000 and y < 0x8000: out.append((i, x - cx, y - cy))
    return out
def click(x, y, how='left'):
    subprocess.run(['python3', os.path.join(PT, 'ravclick.py'), str(x), str(y), how], capture_output=True)
def key(k):
    win = subprocess.run(['xdotool', 'search', '--pid', str(pid)], capture_output=True, text=True).stdout.split()[-1]
    subprocess.run(['xdotool', 'key', '--window', win, k])
def figure(i):
    for j, x, y in objects():
        if j == i: return x + 12, y + 18   # (the place is its square's corner: the body is about 12 right and 18 down)
cmd = sys.argv[1] if len(sys.argv) > 1 else 'state'
if cmd == 'state':
    print('turn', turn(), 'objects', objects())
elif cmd == 'end':
    t = turn(); print('ending turn of', t)
    if t < 4: key('q'); time.sleep(1.5); key('e'); time.sleep(3)   # (Q: its END menu, the manual's key; E: END TURN)
elif cmd == 'until':        # until member N's turn, ending the others' (at most 3 minutes)
    want = int(sys.argv[2]); end = time.time() + 180
    while time.time() < end and turn() != want:
        if turn() < 4: print('ending turn of', turn()); key('q'); time.sleep(1.5); key('e'); time.sleep(3)
        else: time.sleep(1)
    print('turn', turn())
elif cmd == 'wait':
    end = time.time() + int(sys.argv[2])
    while time.time() < end and turn() >= 4: time.sleep(1)
    print('turn', turn())
elif cmd == 'cast':
    x, y, levels = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    me = turn(); mx, my = figure(me)
    foes = sorted((abs(x2 - mx) + abs(y2 - my), i, x2, y2) for i, x2, y2 in objects() if i > 3 and 0 <= x2 < 320 and 0 <= y2 < 200)
    if not foes: sys.exit('no foe on screen')
    d, i, fx, fy = foes[0]
    click(22, 17); time.sleep(2)
    for _ in range(levels): click(197, 171); time.sleep(1.5)
    click(x, y); time.sleep(2); click(fx + 12, fy + 18, "none"); time.sleep(1)
    subprocess.run(['xdotool', 'mousedown', '1']); time.sleep(0.3); subprocess.run(['xdotool', 'mouseup', '1'])
    print('cast by', me, 'at object', i, 'screen', (fx + 12, fy + 18))
