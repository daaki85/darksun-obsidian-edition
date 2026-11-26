# 2026-11-26-ravager-new-spells-fx.py (from playtest/): the sequel's active effects (owner, caster, spell, effect, amount)
import argparse, os, struct, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager, ravlog
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g); load = ds - ravager.DGROUP
names = ravlog.effect_names(g, load)
n = struct.unpack('<H', g.read(ds * 16 + 0x2100, 2))[0]
data = g.read((load + 0x3E71) * 16 + 0x24D, n * 10)
for i in range(n):
    o, c, s = struct.unpack_from('<hhh', data, i * 10)
    e = data[i * 10 + 6]
    print(o, c, s, e, names.get(e, '?'), data[i * 10 + 9], data[i*10:i*10+10].hex())
