# powers.py: each party member's known psionic powers (selector 2F0h's segment, +77h + member x 22h +
# power, bits 3-7: known), by name. Exits 1 while none is known (a new game still loading).
import os,struct,sys
HERE = os.path.dirname(os.path.abspath(__file__)); exec(open(os.path.join(HERE, "live.py")).read())
seg,=struct.unpack('<H', g.read((gd.load_seg+0x4137)*16+0x2F0,2))
out=[]
for m in range(4):
    b=g.read(seg*16+0x77+m*0x22,34)
    out.append([gd.spell_name(138+p) for p,x in enumerate(b) if x>>3])
print(out)
sys.exit(0 if any(out) else 1)
