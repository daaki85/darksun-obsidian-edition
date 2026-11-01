# walkto.py TX TY [TRIES]: walk the party's leader to map position TX, TY (16ths of a square, as
# party_position) with left clicks on the map in Walk mode (the plain arrow pointer; right-click
# cycles it). Screen = map - camera (DS:1178h, x and y words), 1 map unit a pixel. Each click is
# clamped to the open view (not the top bar, not the combat log panel at the bottom right), so far
# targets take several clicks. Prints each step; exits 0 within 12 units, 1 if it stops moving
# (a wall: the dice log says NO PATH FROM HERE). The camera doesn't follow the leader closely: it
# scrolls in steps, so always work from the camera, never from the screen's centre. Over a big
# map the view doesn't follow the leader at all: each step drags it back (scroll.py) when the
# leader is near an edge.
import sys, time, subprocess, struct, os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
tx, ty = int(sys.argv[1]), int(sys.argv[2]); tries = int(sys.argv[3]) if len(sys.argv) > 3 else 12
def pos(): return gd.party_position()
def cam(): return struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
def ok(sx, sy):  # the open view: below the top bar, clear of the log panel (x 130+, y 115+)
    return 4 <= sx <= 315 and 24 <= sy <= 190 and not (sx >= 130 and sy >= 115)
still = 0
for step in range(tries):
    px, py = pos()
    if abs(px - tx) <= 12 and abs(py - ty) <= 12:
        print('ARRIVED', px, py); sys.exit(0)
    cx, cy = cam()
    lx, ly = px - cx, py - cy  # the leader on screen
    if not (60 <= lx <= 260 and 60 <= ly <= 150):  # the view left the leader behind: drag it back
        subprocess.run(['python3', os.path.join(HERE, 'scroll.py'), str(-(lx - 160) * 5 // 4),
                        str(-(ly - 107) * 5 // 4)], capture_output=True)
        cx, cy = cam(); lx, ly = px - cx, py - cy
    sx, sy = tx - cx, ty - cy
    f = 1.0
    while not ok(int(lx + (sx - lx) * f), int(ly + (sy - ly) * f)) and f > 0.05:
        f *= 0.8
    cx_, cy_ = int(lx + (sx - lx) * f), int(ly + (sy - ly) * f)
    subprocess.run(['python3', os.path.join(HERE, 'click.py'), str(cx_), str(cy_)], capture_output=True)
    time.sleep(1.0)
    for _ in range(20):  # until the leader stops
        a = pos(); time.sleep(0.5); b = pos()
        if a == b: break
    nx, ny = pos()
    print(f'step {step}: click {cx_},{cy_} -> {nx},{ny}')
    still = still + 1 if (nx, ny) == (px, py) else 0
    if still >= 2:
        print('STOPPED', nx, ny); sys.exit(1)
print('NOT THERE', *pos()); sys.exit(1)
