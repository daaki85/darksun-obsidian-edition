# healparty.py: each party member's hit points to their sheet's most (memory only: never save after)
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
far = game.far_pointer(g, ds, game.SHEETS_PTR); cbase = game.far_pointer(g, ds, game.CREATURES_PTR)
for index in range(4):
    cr = gd.creature(index); sheetno = struct.unpack_from('<H', cr, 4)[0]
    most = struct.unpack('<H', g.read(far + sheetno * game.SHEET_SIZE + game.SHEET_MAX_HP, 2))[0]
    print(gd.creature_name(index), struct.unpack_from('<H', cr, 0)[0], '->', most)
    g.write(cbase + index * game.CREATURE_SIZE, struct.pack('<H', most))
