# squarewalk.py COL ROW [POINTS]: on a party member's turn in a fight, click the middle of walk-map
# square COL,ROW with whatever pointer is up (pointer.py walk first) and say where the member
# stopped and what movement it has left. With POINTS, a test's memory edit first (never save
# after): the member's movement points set and its "can walk" bit put back, so one turn serves many
# walks. The END menu a spent Move opens is closed with Escape (seen by DS:0BC9h, 2 with a menu up).
import sys, os, struct, time, subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
col, row = int(sys.argv[1]), int(sys.argv[2])
turn = gd.whose_turn()
cr = gd.combatant_creature(turn)
seg = (gd.load_seg + 0x37BD) * 16


def where():
    x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + turn * 32, 4))
    return x >> 4, y >> 4


def points():
    return struct.unpack('<h', g.read(seg + 0x22B + cr * 2, 2))[0]


def menu():
    return g.read(ds * 16 + 0x0BC9, 1)[0] == 2


if menu():
    subprocess.run(['xdotool', 'key', 'Escape']); time.sleep(0.8)
if len(sys.argv) > 3:
    fl, = struct.unpack('<H', g.read(seg + 0x1D5 + cr * 2, 2))
    g.write(seg + 0x1D5 + cr * 2, struct.pack('<H', fl | 1))
    g.write(seg + 0x22B + cr * 2, struct.pack('<h', int(sys.argv[3])))
    at = (gd.load_seg + 0x3972) * 16  # (the walk its Move ran out on forgotten: with the bit back
    g.write(at + 0x377 + turn * 0x1C, b'\xff')  # the game would go on with it)
    g.write(at + 0x8AA + turn * 0x13, b'\0\0')
cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
sx, sy = col * 16 + 8 - cx, row * 16 + 8 - cy
if not (2 <= sx <= 317 and 36 <= sy <= 197):
    sys.exit(f'square {col},{row} is off the view ({sx},{sy})')
start, p0 = where(), points()
subprocess.run([sys.executable, os.path.join(PT, 'click.py'), str(sx), str(sy)], stdout=subprocess.DEVNULL)
t0 = time.monotonic()
while where() == start and time.monotonic() - t0 < 3:  # (the walk can begin a second or two after the click)
    time.sleep(0.05)
last, still = where(), time.monotonic()
while time.monotonic() - t0 < 25:
    time.sleep(0.1)
    now = where()
    if now != last:
        last, still = now, time.monotonic()
    elif time.monotonic() - still > 1.5:
        break
m = menu()
print(f'{gd.creature_name(cr)} {start} -> {last} (clicked {col},{row}{"" if last == (col, row) else ": NOT REACHED"}) '
      f'points {p0} -> {points()}{" END menu" if m else ""} turn {gd.whose_turn()}')
if m:
    subprocess.run(['xdotool', 'key', 'Escape'])
