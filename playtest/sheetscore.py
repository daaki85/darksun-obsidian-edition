# sheetscore.py MEMBER [lv=N] [str= dex= con= int= wis= cha=]: the sheet's first level (+24h) and the
# creature record's scores (+22h on: what the game's DUAL window reads), then race, classes, levels,
# alignment and scores. Memory only: never save after (2026-11-09, the DUAL window's checks).
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
cr = game.far_pointer(g, ds, game.CREATURES_PTR); sh = game.far_pointer(g, ds, game.SHEETS_PTR)
m = int(sys.argv[1]); rec = g.read(cr + m * 0x3A, 0x3A); si = struct.unpack_from('<H', rec, 4)[0]
names = ['str', 'dex', 'con', 'int', 'wis', 'cha']
for a in sys.argv[2:]:
    k, v = a.split('='); v = int(v)
    if k == 'lv': g.write(sh + si * 0x47 + 0x24, bytes((v,)))
    elif k in names: g.write(cr + m * 0x3A + 0x22 + names.index(k), bytes((v,)))
rec = g.read(cr + m * 0x3A, 0x3A); s = g.read(sh + si * 0x47, 0x47)
print('race', s[0x18], 'classes', list(s[0x21:0x24]), 'levels', list(s[0x24:0x27]), 'align', s[0x1A], 'scores', list(rec[0x22:0x28]))
