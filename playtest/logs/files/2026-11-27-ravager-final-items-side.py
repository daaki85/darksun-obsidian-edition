# side.py THING [SIDE]: the creature side (+15h) of combatant THING (the fighters' table), and the game clock.
import argparse,sys,struct
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g=connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()),host_base=None))
ds=game.find_data_segment(g)
t=int(sys.argv[1])
kind,idx=struct.unpack('<BH',g.read((ds+0x3F49-0x47E0)*16+0xC33+3*t,3))
o,s=struct.unpack('<HH',g.read(ds*16+0x19C9,4)); a=s*16+o+idx*0x31
if len(sys.argv)>2: g.write(a+0x15,bytes([int(sys.argv[2])]))
co,cs=struct.unpack('<HH',g.read(ds*16+0x9C0C,4))
print('thing',t,'kind',kind,'creature',idx,'side',g.read(a+0x15,1)[0],'name',g.read(a+0,0)," clock",struct.unpack('<I',g.read(cs*16+co,4))[0])
