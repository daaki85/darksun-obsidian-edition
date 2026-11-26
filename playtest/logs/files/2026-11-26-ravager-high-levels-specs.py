"""Test edit (never saved): MEMBER's weapon specs (the sequel's 48h sheet, +42h-+44h V3 packed, +45h-+47h the four more)
set to KINDS (names from specialize.KINDS), or shown with no KINDS.
  python3 2026-11-26-ravager-high-levels-specs.py MEMBER [KIND,KIND,...]"""
import argparse, os, struct, sys
PT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, specialize, ravlog
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x19C5, 4))
m = int(sys.argv[1]); at = seg * 16 + off + m * 0x48
if len(sys.argv) > 2:
    kinds = [specialize.KINDS.index(k) + 1 for k in sys.argv[2].split(',')]
    roll = game.specs_of(g.read(at + 0x42, 3) + b'\0')[1]   # (the age roll kept)
    g.write(at + 0x42, game.packed_specs(kinds[:4], 0, roll)[:3])
    more = 0
    for i, k in enumerate(kinds[4:]):
        more |= k << (5 * i)
    g.write(at + 0x45, more.to_bytes(3, 'little'))
ravlog.apply_layout()
sheet = g.read(at, 0x48)
print('member %d specs' % m, [specialize.KINDS[k - 1] if k else '-' for k in game.spec_kinds(sheet)], sheet[0x42:0x48].hex(' '))
