# onlywall.py: a test edit (never saved): Ar'Anda knows Wall of Fog (11) alone, 3 casts at every wizard level.
import argparse,sys,struct
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g=connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()),host_base=None))
ds=game.find_data_segment(g)
print('was',[i for i in range(120) if g.read(0x3F3DC,15)[i//8]>>(i%8)&1])
b=bytearray(15); b[1]=1<<3; g.write(0x3F3DC,bytes(b)); g.write(ds*16+0x446A,bytes([3]*9))
print('now',[i for i in range(120) if g.read(0x3F3DC,15)[i//8]>>(i%8)&1])
