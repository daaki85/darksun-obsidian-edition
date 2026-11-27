# 2026-11-27-ravager-arrow-leftovers-know38.py: test-only memory edit (never saved): party member 0 knows Vampiric Touch (38) in the sequel's known bitset
import sys, os, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravarrows
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
class G: pass
gd = G(); gd.ds = game.find_data_segment(g)
at = ravarrows.known_at(gd, 0) + 38 // 8
b = g.read(at, 1)[0]; print('before', hex(b))
if '--write' in sys.argv:
    g.write(at, bytes([b | (1 << (38 % 8))])); print('after', hex(g.read(at, 1)[0]))
