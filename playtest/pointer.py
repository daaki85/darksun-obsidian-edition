# pointer.py [walk|look|attack [X Y]]: the map pointer's mode (DS:11B8h: 1 walk, 2 look (the eye: also talk, use), 4 attack; a right-click cycles 1, 4, 2);
# with a mode, right-clicks at X, Y (bare floor! default 250,185) until the pointer has it.
import os, sys, struct, subprocess, time; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
MODES = {'walk': 1, 'attack': 4, 'look': 2}
mode = lambda: struct.unpack('<H', g.read(ds * 16 + 0x11B8, 2))[0]
if len(sys.argv) > 1:
    want = MODES[sys.argv[1]]
    x, y = (sys.argv[2], sys.argv[3]) if len(sys.argv) > 3 else ('250', '185')
    for _ in range(4):
        if mode() == want:
            break
        subprocess.run([sys.executable, os.path.join(HERE, 'click.py'), x, y, 'right'], timeout=10,
                       stdout=subprocess.DEVNULL)
        time.sleep(0.6)
print('pointer mode', mode())
