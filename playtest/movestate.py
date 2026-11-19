# movestate.py [R]: in a fight, whose turn it is, its square, the movement points it has left
# (37BD:022Bh + creature x 2) and its turn's flags (37BD:01D5h; bit 0: can still walk), and the
# live walk map R squares round it (default 8; '..' floor, '##' 192 and up, else the byte in hex),
# the mover's square as '@@'. With the Loader's module, the squares it marks as in reach as '++'.
import sys, os, struct
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
R = int(sys.argv[1]) if len(sys.argv) > 1 else 8
turn = gd.whose_turn()
print('fight_on', int(gd.fight_on()), 'turn', turn)
if turn is None:
    sys.exit()
cr = gd.combatant_creature(turn)
x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + turn * 32, 4))
seg = (gd.load_seg + 0x37BD) * 16
pts, = struct.unpack('<h', g.read(seg + 0x22B + cr * 2, 2))
flags, = struct.unpack('<H', g.read(seg + 0x1D5 + cr * 2, 2))
rec = gd.creature(cr)
print(f'{gd.creature_name(cr)}: thing {turn} creature {cr} at ({x},{y}) square ({x >> 4},{y >> 4}) '
      f'Move {rec[0x1B]} points {pts} flags {flags:#x} camera {struct.unpack("<hh", g.read(ds * 16 + CAMERA, 4))}')
m = live_map()
marked = set()
try:
    from dsloader import squares
    marked = squares.reach(m, x >> 4, y >> 4, pts if flags & 1 else 0)
except Exception as e:
    print('(no marks:', e, ')')
sx, sy = x >> 4, y >> 4
print('     ' + ''.join(f'{c:3d}'[-3:] for c in range(sx - R, sx + R + 1)))
for row in range(sy - R, sy + R + 1):
    line = f'{row:4d} '
    for col in range(sx - R, sx + R + 1):
        v = m[row * 128 + col] if 0 <= col < 128 and 0 <= row < 98 else 255
        if (col, row) == (sx, sy):
            t = '@@'
        elif (col, row) in marked:
            t = '++' if not v else f'+{v & 15:x}'
        else:
            t = '..' if v == 0 else '##' if v >= 192 else f'{v:02x}'
        line += ' ' + t
    print(line)
