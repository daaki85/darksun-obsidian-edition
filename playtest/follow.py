# follow.py OBJECT [ROUNDS]: keep the party within a few squares of a map object that walks (an
# escort: Kurzak, object 29, leads a new party from the arena's gate to its cell, a waypoint at a
# time, each waiting until the party is within 4 squares: 141 at 0h, INLOS range 4). Each round:
# where the object stands (gd.things_of / thing_square), and route.py to beside it; messages are
# clicked away. Prints each round.
import sys, os, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
obj = int(sys.argv[1]); rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 20
for n in range(rounds):
    if subprocess.run(['sh', os.path.join(HERE, 'msgbox.sh')]).returncode == 0:
        subprocess.run(['sh', os.path.join(HERE, 'boxclick.sh')]); time.sleep(1); continue
    things = gd.things_of(obj)
    if not things: print('object', obj, 'not on the map'); break
    c, r = gd.thing_square(things[0]); px, py = gd.party_position()
    print(f'round {n}: object at square {(c, r)}, party at {(px >> 4, py >> 4)}', flush=True)
    if abs((px >> 4) - c) + abs((py >> 4) - r) > 3:
        subprocess.run(['python3', os.path.join(HERE, 'route.py'), str(c * 16 + 8), str(r * 16 + 24)], capture_output=True)
    time.sleep(4)
