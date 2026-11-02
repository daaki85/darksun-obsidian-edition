# mapshot.py OUT.png [W H]: a picture of the whole region the party is in, W x H map units (default
# 1920 x 1536), made by dragging the view across it (scroll.py) and pasting each 320x200 capture
# (shot.sh) at its camera, the top bar and anything below y 180 left out. One map unit is a pixel,
# so a point's map position is its pixel in the picture: plan walks on it (the party crosses a few
# hundred units a click; a far click says NO PATH FROM HERE). Takes some minutes; no box may be up.
import sys, os, struct, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
out = sys.argv[1]; W = int(sys.argv[2]) if len(sys.argv) > 2 else 1920; H = int(sys.argv[3]) if len(sys.argv) > 3 else 1536
def cam(): return struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
tmp = os.path.join(WORK, 'mapshot-tile.png')
subprocess.run(['convert', '-size', f'{W}x{H}', 'xc:black', out])
for ty in range(0, H, 150):
    for tx in range(0, W, 280):
        subprocess.run(['python3', os.path.join(HERE, 'viewto.py'), str(tx + 160), str(ty + 100)], capture_output=True)
        cx, cy = cam()
        subprocess.run(['sh', os.path.join(HERE, 'shot.sh'), tmp], capture_output=True)
        subprocess.run(['convert', out, '(', tmp, '-crop', '320x160+0+20', '+repage', ')', '-geometry',
                        f'+{cx}+{cy + 20}', '-composite', out])
        print('tile at camera', (cx, cy), flush=True)
print('done', out)
