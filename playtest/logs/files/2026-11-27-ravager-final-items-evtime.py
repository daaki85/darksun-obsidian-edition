# evtime.py THING HANDLE SECONDS: an effect-ends event (kind 7) of THING's HANDLE brought to the clock + SECONDS (a test edit).
import argparse,sys,struct
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g=connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()),host_base=None))
ds=game.find_data_segment(g)
co,cs=struct.unpack('<HH',g.read(ds*16+0x9C0C,4)); now=struct.unpack('<I',g.read(cs*16+co,4))[0]
o,s=struct.unpack('<HH',g.read(ds*16+0x2A63,4)); cnt=struct.unpack('<H',g.read(ds*16+0x2A6B,2))[0]
t,h,d=map(int,sys.argv[1:4])
for i in range(cnt):
    a=s*16+o+0x11*i; r=g.read(a,0x11)
    if r[4]==7 and struct.unpack('<H',r[5:7])[0]==t and r[7]==h:
        print('was',struct.unpack('<I',r[:4])[0],'now',now,'->',now+d); g.write(a,struct.pack('<I',now+d))
