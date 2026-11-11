# doorwatch.py SECONDS: Kurzak's door and the two who use it, printed at each change (every half second):
# the live walk map's square 99,34 (0 open, 192 shut, 96 someone in it), and Kurzak's and
# Legcrusher's map places with their orders (DSUN 3972:08AAh table, objects under 48; None above).
# Run it in the background across a call (logs/2026-11-11-doorway-blocked.md).
import os,struct,sys,time
HERE = os.path.dirname(os.path.abspath(__file__)); exec(open(os.path.join(HERE, "live.py")).read())
base=(0x3972+gd.load_seg)*16+0x08AA
last=None; t0=time.time()
while time.time()-t0<float(sys.argv[1]):
    off, seg = struct.unpack('<HH', g.read(ds*16 + MAP_PTR, 4))
    gr=g.read(seg*16+off+34*128+99,1)[0]
    pos={}
    for t,cc in dict(gd.combatants()).items():
        n=gd.creature_name(cc)
        if n in ('Kurzak','Legcrusher'):
            pos[n]=(struct.unpack('<HH', g.read(ds*16+0x669D+t*32,4)), g.read(base+t*0x13,1)[0] if t<48 else None)
    st=(gr,pos)
    if st!=last: print('%.1f'%(time.time()-t0), gd.game_time(), st, flush=True); last=st
    time.sleep(0.5)
