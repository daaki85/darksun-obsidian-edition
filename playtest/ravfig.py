# ravfig.py [0|1]: Wake of the Ravager's figure shadows (DSCLOG2's FIGURE SHADOWS) in the running game ($WORK/rav.pid): prints the header's fig_shadows (+1960), the floor passes they were drawn in (+1962), the shadows cast (+1964) and the redraws widened (+1966), the frames kept as drawn (+1968) and the shadows cast from them (+1970), the shadows cast from another kept frame of the picture (+1978) and the figures that cast none, their picture out with none kept (+1980), with the walls' passes (+1874), and the dust's switch (+1972, the Loader sets it once LIGHT is made) and puffs laid (+1974); 0 or 1 sets fig_shadows (a same-view toggle of the helper's own switch, no game state: then draw the view again, as ravtone.py's C then Escape).
import os, sys, struct, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'obsidian-edition'))
from dsloader.__main__ import connect
g = connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()), host_base=None))
mem = g.read(0, 0x110000)
i = mem.find(b'DSCLOGR1')
assert i >= 0, 'no DSCLOG2 header'
if len(sys.argv) > 1:
    g.write(i + 1960, struct.pack('<H', int(sys.argv[1])))
on, passes, drawn, wides, kept, from_kept = struct.unpack('<6H', g.read(i + 1960, 12))
walls, = struct.unpack('<H', g.read(i + 1874, 2))
dust_on, puffs, _, other, missed = struct.unpack('<5H', g.read(i + 1972, 10))
print('header %X: fig_shadows %d, passes %d, shadows cast %d, redraws widened %d, frames kept %d, cast from kept %d (another frame %d), none for want of one %d; wall passes %d; dust_on %d, puffs %d' % (i, on, passes, drawn, wides, kept, from_kept, other, missed, walls, dust_on, puffs))
