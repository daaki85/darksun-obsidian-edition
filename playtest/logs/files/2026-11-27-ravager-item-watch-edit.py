# 2026-11-27-ravager-item-watch-edit.py IDX word0|type VALUE: a test edit (never saved) of the running sequel's
# item record IDX: its +0 word (0: the record freed, as the game frees one) or its type (+0Ah). Prints the
# record before and after. Run from playtest/ (logs/2026-11-27-ravager-item-watch.md).
import sys, os, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
o, s = struct.unpack('<HH', g.read(ds*16 + 0x19C1, 4)); it = s*16 + o   # (the sequel's item table)
idx, field, val = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
rec = it + idx*0x17
print('before', g.read(rec, 0x17).hex(' '))
g.write(rec + (0 if field == 'word0' else 0x0A), struct.pack('<H', val))
print('after ', g.read(rec, 0x17).hex(' '))
