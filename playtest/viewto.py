# viewto.py X Y: drag the view (scroll.py, the middle button) until map point X, Y is near the
# screen's centre, so a far spot can be clicked: the party then walks there by itself, finding its
# own way (it does over a whole region, if the spot is floor). Prints the camera and where the
# point is on screen.
import sys, os, struct, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
tx, ty = int(sys.argv[1]), int(sys.argv[2])
def cam(): return struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
for _ in range(25):
    cx, cy = cam(); sx, sy = tx - cx, ty - cy
    if 100 <= sx <= 220 and 70 <= sy <= 140: break
    subprocess.run(['python3', os.path.join(HERE, 'scroll.py'), str(-(sx - 160) * 5 // 4), str(-(sy - 107) * 5 // 4)],
                   capture_output=True)
cx, cy = cam(); print('camera', (cx, cy), 'point on screen', (tx - cx, ty - cy))
