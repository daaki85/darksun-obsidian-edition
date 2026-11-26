# 2026-11-26-ravager-pick-pockets-hdr.py: DSCLOG2's PICK POCKETS words and the game's pointer mode in the running sequel
import sys, os, struct, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravlog
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
low = g.read(0, 0x110000)
at = low.find(ravlog.HDR_SIG)
while at % 16: at = low.find(ravlog.HDR_SIG, at + 1)
w = lambda o: struct.unpack_from('<H', low, at + o)[0]
names = ['on','seq','reply','who','thief','taken','off','shown','armed','late']
print('hdr %x' % at, ' '.join('%s=%d' % (n, w(2000 + 2 * i)) for i, n in enumerate(names)), 'rules=%#x' % w(170))
ds = game.find_data_segment(g)
print('pointer mode', struct.unpack_from('<H', low, ds * 16 + 0x1440)[0], 'element', struct.unpack_from('<H', low, ds*16+0x9C1C)[0])
off = w(2012); t = low[at - w(20) + off:][:240].split(b'\0')[0]; print('text:', t)
print('pp_armed', low[at + 0xC804])
