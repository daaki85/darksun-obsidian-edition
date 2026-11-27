# 2026-11-27-ravager-defiler-crobj.py [N OBJ]: the sequel's creatures 0-127 (name, HP, status, object +6); with N OBJ, creature N's
# object word set to -OBJ (a test edit, never saved)
import sys, struct, argparse
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
o, s = struct.unpack('<HH', g.read(ds*16 + 0x19C9, 4)); cr = s*16 + o
if len(sys.argv) > 2:
    n, obj = int(sys.argv[1]), int(sys.argv[2])
    g.write(cr + n*0x31 + 6, struct.pack('<h', -obj))
for n in range(0, 128):
    r = g.read(cr + n*0x31, 0x31)
    name = r[0x21:0x31].split(b'\0')[0]
    if name:
        print(n, name.decode('latin1'), 'hp', struct.unpack_from('<h', r, 0)[0], 'status', r[0x14],
              'obj', -struct.unpack_from('<h', r, 6)[0], 'lists', struct.unpack_from('<hhh', r, 8))
