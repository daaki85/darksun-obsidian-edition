# figcheck.py [LABEL]: are the party's figures drawn? A window grab, then DSCLOG's VIEW_REDRAW
# (header +242: the whole view drawn again, as the game does), a second grab, and for each member
# the pixels changed in a box round its figure (feet at its map place less the camera; 24 x 40
# game pixels above them). A figure missing before the redraw shows as a big count (hundreds);
# drawn, near 0. Grabs kept as $WORK/fc-LABEL-a.png / -b.png.
import os, sys, struct, subprocess, time
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
from PIL import Image, ImageChops
label = sys.argv[1] if len(sys.argv) > 1 else 'x'
W = subprocess.run(['xdotool', 'search'] + os.environ.get('WINQ', '--class dosbox').split(),
                   capture_output=True, text=True).stdout.split()[0]
def grab(p):
    subprocess.run(['import', '-window', W, p], check=True)
    return Image.open(p).convert('RGB')
mem = g.read(0xC0000, 0x40000)
hdr = 0xC0000 + next(i for i in range(0, len(mem), 16) if mem[i:i + 8] == b'DSCLOGva')
a = grab(f'{WORK}/fc-{label}-a.png')
cx, cy = struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))
g.write(hdr + 242, struct.pack('<H', 1))
time.sleep(0.8)
b = grab(f'{WORK}/fc-{label}-b.png')
d = ImageChops.difference(a, b).convert('L').point(lambda v: 255 if v > 24 else 0)
total = sum(1 for v in d.get_flattened_data() if v)
res = []
for m in range(4):
    x, y = struct.unpack('<hh', g.read(ds * 16 + 0x669D + m * 32, 4))
    sx, sy = x - cx, y - cy
    box = (max(sx - 12, 0), max(int((sy - 40) * 1.2), 0), min(sx + 12, 320), min(int((sy + 4) * 1.2), 240))
    if box[0] >= box[2] or box[1] >= box[3]:
        res.append(f'm{m} off'); continue
    c = sum(1 for v in d.crop(box).get_flattened_data() if v)
    res.append(f'm{m}@{sx},{sy}:{c}')
print(f'{label}: changed {total} | ' + ' '.join(res))
