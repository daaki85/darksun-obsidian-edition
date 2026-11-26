# squaresweep.py POINTS [all|edge|out][here] [MAX]: the Loader's squares in reach (dsloader/squares.py)
# against the game, on a party member's turn in a fight, from where its turn began. For each
# square tried: the member's points set to POINTS and its "can walk" bit put back (a test's memory
# edit: never save after), one click on the square, where the member stopped, then F10 (the game's
# own key: the move taken back). 'edge' (default): the marked squares no step leads on from (the
# far rim: the last 10 points' worth); 'all': every marked square; 'out': unmarked free squares beside a marked one (none
# should be reached). Only squares on the view, clear of the name box and of the figures drawn
# over them, are tried. Prints each
# walk and a count: reached in one click, stopped short (the game's own route was longer). With
# 'here' after the kind (edgehere, outhere, allhere) the sweep is from where the member stands now,
# walked back to after each try (points in memory again), not from where its turn began.
import sys, os, struct, time, subprocess
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
from dsloader import squares
P = int(sys.argv[1]); which = sys.argv[2] if len(sys.argv) > 2 else 'edge'
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 999
turn = gd.whose_turn(); cr = gd.combatant_creature(turn)
seg = (gd.load_seg + 0x37BD) * 16


def where():
    x, y = struct.unpack('<HH', g.read(ds * 16 + game.POSITIONS + turn * 32, 4))
    return x >> 4, y >> 4


def points():
    return struct.unpack('<h', g.read(seg + 0x22B + cr * 2, 2))[0]


def arm():
    fl, = struct.unpack('<H', g.read(seg + 0x1D5 + cr * 2, 2))
    g.write(seg + 0x1D5 + cr * 2, struct.pack('<H', fl | 1))
    g.write(seg + 0x22B + cr * 2, struct.pack('<h', P))
    forget()


def forget():
    """The walk the member's Move ran out on forgotten (its next step, 3972:0377h + thing x 1Ch,
    and what it is doing, 3972:08AAh + thing x 13h): with the bit put back the game would go on
    with it, from wherever F10 put the member."""
    at = (gd.load_seg + 0x3972) * 16
    g.write(at + 0x377 + turn * 0x1C, b'\xff')
    g.write(at + 0x8AA + turn * 0x13, b'\0\0')


def menu():
    return g.read(ds * 16 + 0x0BC9, 1)[0] == 2


def settle(begun, limit=25):
    """Where the member stops: the walk can begin a second or two after the click."""
    t0 = time.monotonic()
    while where() == begun and time.monotonic() - t0 < 3:
        time.sleep(0.05)
    last, still = where(), time.monotonic()
    while time.monotonic() - t0 < limit:
        time.sleep(0.1)
        now = where()
        if now != last:
            last, still = now, time.monotonic()
        elif time.monotonic() - still > 1.5:
            break
    return last


HERE = which.endswith('here')  # from where the member stands, walked back to after each try
which = which.replace('here', '') or 'edge'


def click(col, row):
    cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
    subprocess.run([sys.executable, os.path.join(PT, 'click.py'), str(col * 16 + 8 - cx), str(row * 16 + 8 - cy)],
                   stdout=subprocess.DEVNULL)


def back():
    if menu():
        subprocess.run(['xdotool', 'key', 'Escape']); time.sleep(0.6)
    if HERE:
        if where() != start:
            P0 = P
            globals()['P'] = 400
            arm(); globals()['P'] = P0
            click(*start); settle(where())
    else:
        subprocess.run(['xdotool', 'key', 'F10']); time.sleep(0.8)


if menu():
    subprocess.run(['xdotool', 'key', 'Escape']); time.sleep(0.6)
start = where()
if not HERE:
    back()
    arm(); settle(where(), 8); back()  # (a click still waiting from before is walked now, not in the first try)
    start = where()
grid = live_map()
marked = squares.reach(grid, start[0], start[1], P)
cost = squares.costs(grid, start[0], start[1], P + 40)
if which == 'all':
    todo = sorted(marked)
elif which == 'out':
    todo = sorted({(x + dx, y + dy) for x, y in marked for dx in (-1, 0, 1) for dy in (-1, 0, 1)}
                  - marked - {start})
    todo = [s for s in todo if squares.free(grid, s[0], s[1])]
else:
    todo = sorted(s for s in marked if cost.get(s, 999) > P - 10)
ok = short = other = 0
for col, row in todo[:limit]:
    cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))  # (the view can move with the member)
    sx, sy = col * 16 + 8 - cx, row * 16 + 8 - cy
    if not (4 <= sx <= 315 and 38 <= sy <= 196) or (sx > 210 and sy < 40):
        continue
    if any(grid[min(97, row + d) * 128 + col] & 0x20 for d in (1, 2)) or (col, row + 1) == start or (col, row + 2) == start:
        continue  # (a figure stands just south: the click would be on it, an attack or its menu)
    arm()
    click(col, row)
    end = settle(start)
    left = points(); c = cost.get((col, row))
    if end == (col, row):
        ok += 1; word = 'reached'
    elif end == start:
        other += 1; word = 'NO WALK'
    else:
        short += 1; word = f'STOPPED at {end}'
    print(f'{col},{row} (shortest {c}): {word}, {P} -> {left}', flush=True)
    back()
    if where() != start:
        time.sleep(1.5); back()
        if where() != start:
            sys.exit(f'F10 did not bring the member back: at {where()}, began {start}')
print(f'{which} from {start} with {P}: {ok} reached, {short} stopped short, {other} not walked; marked {len(marked)}')
