# ravinvfig.py [FIG C1 C2 C3 [RACE]]: Wake of the Ravager: the creature named $WHO (default Thy, a name's start) its figure (+10h:
# 0 human man ... 13 thri-kreen) and its sheet's classes (+1Bh, 1-17) and race (+12h) printed, or set. Memory only: never save after.
import sys, os, struct, argparse
PT=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read())
g=connect(argparse.Namespace(pid=pid, host_base=None)); ds=game.find_data_segment(g)
off,seg=struct.unpack('<HH',g.read(ds*16+0x19C9,4))
NAME=os.environ.get('WHO','Thy').encode()
b=g.read(seg*16+off,0x31*80)
who=next(i for i in range(80) if b[i*0x31+0x21:i*0x31+0x31].startswith(NAME))
cr=seg*16+off+who*0x31
soff,sseg=struct.unpack('<HH',g.read(ds*16+0x19C5,4)); sh_no,=struct.unpack('<H',g.read(cr+4,2)); sh=sseg*16+soff+sh_no*0x48
fig,=struct.unpack('<H',g.read(cr+0x10,2)); race=g.read(sh+0x12,1)[0]; cls=list(g.read(sh+0x1B,3))
print('who',who,'fig',fig,'race',race,'classes',cls)
if len(sys.argv)>1:
    g.write(cr+0x10,struct.pack('<H',int(sys.argv[1])))
    if len(sys.argv)>2: g.write(sh+0x1B,bytes(int(a) for a in sys.argv[2:5]))
    if len(sys.argv)>5: g.write(sh+0x12,bytes((int(sys.argv[5]),)))
