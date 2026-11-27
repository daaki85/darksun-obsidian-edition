# The sequel's effect records (owner, caster, spell, effect, handle, charges, extra) and its "effect ends" events.
import argparse,os,sys,struct
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g=connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()),host_base=None))
ds=game.find_data_segment(g); load=ds-0x47E0
n=struct.unpack('<H',g.read(ds*16+0x2100,2))[0]
base=(load+0x3E71)*16+0x24D
for i in range(min(n,60)):
    r=g.read(base+10*i,10); o,c,sp,e,h,ch,x=struct.unpack('<HHHBBBB',r)
    print('owner',o,'caster',c,'spell',sp,'effect',e,'handle',h,'charges',ch,'extra',x)
o,s=struct.unpack('<HH',g.read(ds*16+0x2A63,4)); cnt=struct.unpack('<H',g.read(ds*16+0x2A6B,2))[0]
print('events',cnt)
for i in range(min(cnt,80)):
    r=g.read(s*16+o+0x11*i,0x11); 
    if r[4]==7: print(' ends: when',struct.unpack('<I',r[:4])[0],'thing',struct.unpack('<H',r[5:7])[0],'handle',r[7])
