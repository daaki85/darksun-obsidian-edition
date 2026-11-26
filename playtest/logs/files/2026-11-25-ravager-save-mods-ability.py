# 2026-11-25-ravager-save-mods-ability.py CREATURE [ABILITY VALUE]: a creature's six abilities (STR DEX CON INT WIS CHA at
# its record's +19h), and a test edit of one (0-5; never saved): Ester's DEX lowered so the cahulaks' heads cost to hit.
import sys, struct, argparse, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds * 16 + ravager.CREATURES_PTR, 4))
at = seg * 16 + off + int(sys.argv[1]) * ravager.CREATURE_SIZE + 0x19
print('abilities', list(g.read(at, 6)))
if len(sys.argv) > 3:
    g.write(at + int(sys.argv[2]), bytes((int(sys.argv[3]),))); print('now', list(g.read(at, 6)))
