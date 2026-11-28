# dragonsbane-save.py SRC DST: a copy of an SL save with Dragonsbane (SL object 2605, +4) in Jenna's backpack
# (item 87; links and slot kept), for logs/2026-11-27-dragonsbane-metal.md
import sys, struct, os; sys.path.insert(0,'/home/claude/darksun-obsidian-edition/obsidian-edition'); sys.path.insert(0,'/home/claude/darksun-obsidian-edition/playtest/logs/files')
from dsloader import gff, icons, ravitems
from importlib import import_module; member_items = import_module("2026-11-27-weapon-materials-items").member_items
src, dst = sys.argv[1], sys.argv[2]
data = open(src,'rb').read(); s = gff.read_gff(data)
o = gff.read_gff(open('/tmp/playtest/inst/SEGOBJEX.GFF','rb').read())
items = bytearray(s[('SAVE', 7)]); n = 87
new = bytearray(ravitems._first_record(o, 2605)[:0x15]); old = items[n*0x15:(n+1)*0x15]
for at in (4, 5, 8, 9, 0x11): new[at] = old[at]
items[n*0x15:(n+1)*0x15] = new
open(dst,'wb').write(icons.with_chunks(data, {('SAVE', 7): bytes(items)}))
for m,(name,got) in member_items(gff.read_gff(open(dst,'rb').read())).items():
    print(name, [(n, -struct.unpack_from('<h',it,0)[0], struct.unpack_from('<H',it,0x0A)[0], it[0x11], it[0x14]) for n,it in got])
