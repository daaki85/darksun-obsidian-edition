# randout.py N [SEED]: N random outfit changes for member 0: each time one of its worn items (slot
# under 12) taken off (slot byte +11h set to 50) or put back, waiting for the Loader's copy of
# SEGOBJEX.GFF to be written; every 10th change (and any with the figure not drawn) a line: the
# dressings so far, the picture slots taken, the STALE ones, the store's end, drawn or not. Puts
# every item back at the end. Memory edit: never save after (logs/2026-11-09-picture-store-fix.md).
import os,sys,struct,time,random
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from dsloader import game, sprites
random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 1)
items = game.far_pointer(g, ds, game.ITEMS_PTR)
orig = {i: item[game.ITEM_SLOT] for i, item, t in gd._worn(0) if item[game.ITEM_SLOT] < 12}
orig = dict(list(orig.items())[:5])
copy=os.path.join(PT, '..', 'obsidian-edition', 'dos', 'SEGOBJEX.GFF')
state={i:True for i in orig}; nd=0
def stat():
    n=struct.unpack('<H',g.read(ds*16+0x1F84,2))[0]; tab=g.read((gd.load_seg+0x3E60)*16,n*16)
    e=[struct.unpack_from('<HIiIBB',tab,k*16) for k in range(n)]
    drawn=[not g.read(ds*16+0x6694+c*32,1)[0]&0x80 for c,cr in gd.combatants().items() if cr==0]
    return n,sum(1 for x in e if x[0]==0xFFFE),e[-1][2]+e[-1][1],drawn
try:
  for k in range(int(sys.argv[1])):
    i=random.choice(list(orig)); state[i]=not state[i]
    before=os.stat(copy).st_mtime_ns
    g.write(items+i*game.ITEM_SIZE+game.ITEM_SLOT, bytes([orig[i] if state[i] else 50]))
    t0=time.time()
    while os.stat(copy).st_mtime_ns==before and time.time()-t0<4: time.sleep(0.05)
    nd+= os.stat(copy).st_mtime_ns!=before
    time.sleep(0.5)
    n,s,end,dr=stat()
    if k%10==9 or not all(dr): print(k+1,'dressed',nd,'slots',n,'stale',s,'end',end,'drawn',dr,flush=True)
finally:
  for i,v in orig.items(): g.write(items+i*game.ITEM_SIZE+game.ITEM_SLOT, bytes([v]))
