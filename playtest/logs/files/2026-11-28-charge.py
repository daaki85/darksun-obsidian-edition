import sys, struct, argparse
sys.path.insert(0, '/home/claude/darksun-obsidian-edition/obsidian-edition')
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
o, s = struct.unpack('<HH', g.read(ds*16 + 0x19C1, 4)); it = s*16+o
n = int(sys.argv[1]); a = it + n*0x17
if len(sys.argv) > 2:
    g.write(a+0x0E, struct.pack('<H', int(sys.argv[2]))); g.write(a+0x10, struct.pack('<H', int(sys.argv[3])))
r = g.read(a, 0x17); print('item', n, 'charges', struct.unpack('<H', r[0x0E:0x10])[0], 'power', struct.unpack('<H', r[0x10:0x12])[0], 'slot', r[0x13], r.hex(' '))
