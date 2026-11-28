# The party on the map in Wake of the Ravager (the running game, $WORK/rav.pid): each party thing's draw list entry (x, y, height, flags), its map thing's byte +7 and word +8, its place, its picture (the cache slot's number) and frame, and that frame's width and height when in memory. Run from playtest/.
import sys, os, struct, argparse
PT='/home/claude/darksun-obsidian-edition/playtest'; sys.path.insert(0, os.path.join(PT,'..','obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
pid=int(open('/tmp/playtest/rav.pid').read())
g=connect(argparse.Namespace(pid=pid,host_base=None)); ds=game.find_data_segment(g)
rd=lambda a,n: g.read(a,n)
w=lambda off: struct.unpack('<H', rd(ds*16+off,2))[0]
cx,cy=struct.unpack('<HH', rd(ds*16+0x1408,4))
print('cam',cx,cy)
lo,ls=struct.unpack('<HH', rd(ds*16+0x67B7,4)); n=w(0x264E)
cache=((ds-(0x47E0-0x42A2))&0xFFFF)*16+0x0CA8
for e in range(n):
    x,y,h,fl,t=struct.unpack('<HHBBH', rd(ls*16+lo+8*e,8))
    if t>=8: continue
    m=rd(ds*16+0x67BB+0x25*t,0x25)
    b7=m[7]; w8,=struct.unpack_from('<H',m,8); slot,=struct.unpack_from('<H',m,0x10); fr=m[0x12]
    num,ln,place,off,seg,flg=struct.unpack('<HIIHHB', rd(cache+16*slot,15))
    print('entry',e,'thing',t,'xy',x,y,'h',h,'fl',hex(fl),'b7',b7,'w8',w8,'mx',struct.unpack_from('<HH',m,3),'slot',slot,'pic',num,'frame',fr,'inmem',flg&2)
    if flg&2:
        base=seg*16+off; cnt,=struct.unpack('<H',rd(base+4,2))
        fo,=struct.unpack('<I',rd(base+6+4*fr,4)); fw,fh=struct.unpack('<HH',rd(base+fo,4))
        print('   frames',cnt,'frame w h',fw,fh)
