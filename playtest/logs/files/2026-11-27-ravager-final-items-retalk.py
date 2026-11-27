# test edit: every talk trigger made (PLACE, SCRIPT) (or put back from the saved file)
import argparse,sys,struct,json,os
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g=connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'rav.pid')).read()),host_base=None))
ds=game.find_data_segment(g); load=ds-0x47E0
o,s=struct.unpack('<HH',g.read(ds*16+0x40C0,4)); base=s*16+o
SAVE=os.path.join(os.environ.get('PLAYTEST_WORK', '/tmp/playtest'), 'talk-orig.json')
i=struct.unpack('<H',g.read((load+0x3C10)*16+0xF,2))[0]; recs=[]
while i!=0xFFFF:
    r=g.read(base+13*i,13); recs.append((i,)+struct.unpack_from('<HH',r)); i=struct.unpack_from('<H',r,0xB)[0]
if sys.argv[1]=='back':
    for i,pl,sc in json.load(open(SAVE)): g.write(base+13*i,struct.pack('<HH',pl,sc))
    print('put back',len(recs))
else:
    if not os.path.exists(SAVE): json.dump(recs,open(SAVE,'w'))
    for i,_,_ in recs: g.write(base+13*i,struct.pack('<HH',int(sys.argv[1]),int(sys.argv[2])))
    print('set',len(recs))
