# roster.py RAVFOLDER DOS: each transferred member's items: object, type, the type's kind and material
import sys, struct; sys.path.insert(0, sys.argv[3] if len(sys.argv) > 3 else '/home/claude/darksun-obsidian-edition/obsidian-edition')
from dsloader import gff, dataitems, ravager, ravitems, ravtransfer as rt, specialize
F, D = sys.argv[1], sys.argv[2]
ch = gff.read_gff(open(F + '/CHARSAVE.GFF','rb').read())
seq = rt.load_sequel(F); objs = dict(seq.objects); objs.update(ravager.read_added(D))
tab = ravager.mod_types_table(ravager.materialled_table(seq.objects[ravager.TYPES_CHUNK]))
rk = ravager.rav_kinds(); MAT={-1:'none',0:'wood',1:'bone',2:'stone',3:'obsidian',4:'metal',5:'leather'}
for k in sorted(ch):
    if k[0] != 'CHAR' or k[1] < 32: continue
    recs, _ = dataitems.records(ch[k])
    if not any(r.kind == dataitems.ITEM for r in recs): continue
    name = recs[0].data[0x21:0x30].split(b'\0')[0].decode()
    out = []
    for r in recs:
        if r.kind != dataitems.ITEM: continue
        obj = -struct.unpack_from('<h', r.data, 0)[0]; t, = struct.unpack_from('<H', r.data, 0x0A)
        if t in rk: out.append(f"{obj}:{t} {specialize.KINDS[rk[t]]} {MAT[ravitems.wotr_material(tab, t)]} +{r.data[0x16]} slot{r.data[0x13]}")
    print(k[1], name); [print('   ', x) for x in out]
