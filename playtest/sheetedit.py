# sheetedit.py MEMBER [levelN=V] [flags|=V] [flags=V]: show (and change) party member MEMBER's
# character sheet: its three classes and levels and its class flags word (+12h; 40h the
# gladiator). Memory only: never save the game with a change in; reload to undo.
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import game
member = int(sys.argv[1])
rec = gd.creature(member)
index = struct.unpack_from('<H', rec, 4)[0]
at = game.far_pointer(g, ds, 0x1661) + index * game.SHEET_SIZE
for arg in sys.argv[2:]:
    if arg.startswith('flags|='):
        f = struct.unpack('<H', g.read(at + game.SHEET_FLAGS, 2))[0] | int(arg[7:], 0)
        g.write(at + game.SHEET_FLAGS, struct.pack('<H', f))
    elif arg.startswith('flags='):
        g.write(at + game.SHEET_FLAGS, struct.pack('<H', int(arg[6:], 0)))
    elif arg.startswith('level'):
        k, v = arg[5:].split('='); g.write(at + game.SHEET_LEVELS + int(k), bytes([int(v)]))
sheet = g.read(at, game.SHEET_SIZE)
print(f'#{member} sheet {index} at {at:X}: classes {[sheet[game.SHEET_CLASSES + i] for i in range(3)]} '
      f'levels {[sheet[game.SHEET_LEVELS + i] for i in range(3)]} flags {struct.unpack_from("<H", sheet, game.SHEET_FLAGS)[0]:04x} '
      f'race {sheet[game.SHEET_RACE]} counted AC {gd.counted_ac(member)}')
