# 2026-11-26-codex-review-air-cleric.py OBSIDIAN_DIR: a test edit (never saved) in the running sequel: the second party
# member (Terrannus in the opening party) made an air cleric (sheet +1Bh class 1; 1-4 the clerics of air, earth,
# fire, water) of 18th level (+1Eh) with 3 priest casts at every level (DS:4474h + 22h a member + the level).
import sys, struct, argparse
sys.path.insert(0, sys.argv[1])
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
o, s = struct.unpack('<HH', g.read(ds*16 + 0x19C5, 4))
m = 1; sh = s*16+o+m*0x48
g.write(sh+0x1B, bytes([1])); g.write(sh+0x1E, bytes([18]))
g.write(ds*16+0x4474+0x22*m+1, bytes([3]*9))
print(g.read(sh+0x1B, 6).hex(' '), g.read(ds*16+0x4474+0x22*m, 10).hex(' '))
