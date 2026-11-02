# scroll.py DX DY: drag the map view with the middle mouse button by DX, DY game pixels (the
# user's advice, 2026-11-01): the way to see past walls, where the view won't scroll by itself.
# Dragging down shows more of the north (the camera's y falls: 60 pixels moved it 48, in steps
# of 16), as if grabbing the map. Which way the view moves for a given drag is printed (the camera before and after), so check it.
# Then click the spot (walkto.py, or click.py on the screen position) and the party walks there.
import sys, os, time, subprocess, struct
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
dx, dy = int(sys.argv[1]), int(sys.argv[2])
def cam(): return struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
# The pointer must never reach the screen's edge: there the view scrolls by itself, the other
# way (a 150-pixel drag from the centre sent it south, 2026-11-01). So start from the side the drag
# moves away from, keep the whole drag within 16..304 x 30..184, and cap it to that.
dx = max(-270, min(270, dx)); dy = max(-150, min(150, dy))
x0 = 160 - dx // 2; y0 = 107 - dy // 2
before = cam()
subprocess.run(['python3', os.path.join(PT, 'click.py'), str(x0), str(y0), 'none'], capture_output=True)
subprocess.run(['xdotool', 'mousedown', '2']); time.sleep(0.2)
steps = 8
for _ in range(steps):
    subprocess.run(['xdotool', 'mousemove_relative', '--', str(dx // steps), str(dy // steps)]); time.sleep(0.12)
time.sleep(0.2); subprocess.run(['xdotool', 'mouseup', '2']); time.sleep(0.3)
# then every button released: after a drag the game took no clicks until they were (2026-11-01)
for b in '1', '2', '3':
    subprocess.run(['xdotool', 'mouseup', b], capture_output=True)
time.sleep(0.5)
print('camera', before, '->', cam())
