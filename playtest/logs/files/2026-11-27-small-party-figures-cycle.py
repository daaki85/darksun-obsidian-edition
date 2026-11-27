# Test tool (2026-11-27-small-party-figures.md): # Cycle party member M through every figure x class, reopening the inventory, grabbing the column.
import os, sys, struct, time, subprocess
PT='/home/claude/darksun-obsidian-edition/playtest'; sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game
S = sys.argv[1]; m = int(sys.argv[2]); figs = [int(x) for x in sys.argv[3].split(',')]
GC = {1: 1, 2: 5, 3: 9, 4: 10, 5: 11, 6: 12, 7: 13, 8: 17}
W = subprocess.check_output(['xdotool', 'search', '--class', 'dosbox']).split()[0].decode()
cre = game.far_pointer(g, ds, 0x1665) + m * 0x3A
idx = struct.unpack('<H', g.read(cre + 4, 2))[0]
sh = game.far_pointer(g, ds, game.SHEETS_PTR) + idx * game.SHEET_SIZE
orig_fig = g.read(cre + 0x18, 2); orig_race = g.read(sh + 0x18, 1); orig_cls = g.read(sh + 0x21, 3)
mem0 = g.read(0xA0000, 0x60000)
hdr = 0xA0000 + next(i for i in range(0, len(mem0), 16) if mem0[i:i+8] == b'DSCLOGvf')
def key(k):
    subprocess.run(['xdotool', 'key', '--window', W, k]); time.sleep(0.4)
try:
    for f in figs:
        race = f // 2 + 1 if f < 12 else f - 5
        for c in range(1, 9):
            g.write(cre + 0x18, struct.pack('<H', f)); g.write(sh + 0x18, bytes([race]))
            g.write(sh + 0x21, bytes([GC[c], 0, 0]))
            time.sleep(1.8)
            key('Escape'); time.sleep(0.8); key('i'); time.sleep(2.2)
            pics = struct.unpack('<4H', g.read(hdr + 1893, 8))
            out = f'{S}/cyc/f{f:02d}c{c}.png'
            subprocess.run(['import', '-window', W, out])
            print(f, c, 'small_pics', pics, flush=True)
finally:
    g.write(cre + 0x18, orig_fig); g.write(sh + 0x18, orig_race); g.write(sh + 0x21, orig_cls)
    print('restored', flush=True)
