import sys, struct, os; sys.path.insert(0,'/home/claude/darksun-obsidian-edition/obsidian-edition'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dsloader import gff, icons, ravitems
from importlib import import_module; member_items = import_module("2026-11-27-weapon-materials-items").member_items
src, dst = sys.argv[1], sys.argv[2]
data = open(src,'rb').read(); s = gff.read_gff(data)
o = gff.read_gff(open('/tmp/playtest/inst/SEGOBJEX.GFF','rb').read())
tmpl = lambda obj: bytearray(ravitems._first_record(o, obj)[:0x15])
def made(obj, typ, name, value, plus):
    r = tmpl(1012); struct.pack_into('<h', r, 0, -obj); struct.pack_into('<H', r, 6, value)
    struct.pack_into('<H', r, 0x0A, typ); struct.pack_into('<H', r, 0x12, name); r[0x14] = plus; return r
want = {86: made(2724, 158, 0x174, 20800, 1), 87: tmpl(1185), 35: made(2722, 157, 0x175, 20800, 1),
        243: made(2696, 154, 0x174, 500, 0), 241: tmpl(1018), 2: made(2698, 155, 0x175, 150, 0),
        8: made(2700, 156, 0x178, 150, 0), 290: tmpl(1577), 134: tmpl(2041)}
items = bytearray(s[('SAVE', 7)])
for n, new in want.items():
    old = items[n*0x15:(n+1)*0x15]
    for at in (4, 5, 8, 9, 0x11):  # (the list's links and the slot kept)
        new[at] = old[at]
    items[n*0x15:(n+1)*0x15] = new
open(dst,'wb').write(icons.with_chunks(data, {('SAVE', 7): bytes(items)}))
for m,(name,got) in member_items(gff.read_gff(open(dst,'rb').read())).items():
    print(name, [(n, -struct.unpack_from('<h',it,0)[0], struct.unpack_from('<H',it,0x0A)[0], it[0x11], it[0x14]) for n,it in got])
