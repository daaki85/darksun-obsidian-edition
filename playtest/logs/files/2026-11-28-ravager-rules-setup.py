import sys, struct, argparse
sys.path.insert(0, '/home/claude/darksun-obsidian-edition/obsidian-edition')
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
def far(a): o, s = struct.unpack('<HH', g.read(ds*16 + a, 4)); return s*16 + o
sh, cr, it = far(0x19C5), far(0x19C9), far(0x19C1)
for m in range(4): g.write(sh + m*0x48 + 0x21, bytes((0xF6,)))           # base AC -10
g.write(sh + 2*0x48 + 0x1B, bytes((7,))); g.write(sh + 2*0x48 + 0x1E, bytes((18,)))   # Thy'rokh fire druid 18
g.write(ds*16 + 0x446A + 0x22*2 + 0x0B, bytes([3]*9))
v = g.read(cr + 1*0x31 + 9, 1)[0]; g.write(cr + 1*0x31 + 9, bytes((v | 4,)))     # Terrannus Protected vs Energy
g.write(cr + 1*0x31, struct.pack('<H', 20))                                   # ... at 20 HP
a = it + 13*0x17                                                              # Gerakis's weapon: Magic Missile, 1 charge, +15
g.write(a + 0x0E, struct.pack('<H', 1)); g.write(a + 0x10, struct.pack('<H', 9)); g.write(a + 0x16, bytes((15,)))
print('set: Terrannus +9', hex(g.read(cr+0x31+9,1)[0]), 'HP', struct.unpack('<H', g.read(cr+0x31,2))[0],
      '; item 13', g.read(a, 0x17).hex(' '))
