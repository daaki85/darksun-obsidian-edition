# pixmatch.py X Y R G B [X Y R G B ...]: exit 0 if every named pixel of a fresh 320x240 window
# grab is that colour, within 3 a channel and one row up or down. The tolerance is for the
# recompiled program (PT_TARGET=recomp): its VGA colours differ from DOSBox's by one (38 of 63
# is 153 there, 154 in DOSBox) and its 320x200 picture is scaled to the 240 rows a row apart.
import sys, os, subprocess, io
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import WORK  # noqa (sets DISPLAY)
try:
    from PIL import Image
except ImportError:  # (a container whose PIL is broken: "cannot import name '_imaging'", 2026-11-01)
    Image = None
winq = os.environ.get('WINQ', '--class dosbox').split()
w = subprocess.run(['timeout', '5', 'xdotool', 'search'] + winq, capture_output=True, text=True).stdout.split()
if not w:
    print('no window'); sys.exit(2)
png = subprocess.run(['timeout', '10', 'import', '-window', w[0], 'png:-'], capture_output=True).stdout
vals = [int(v) for v in sys.argv[1:]]
if Image is not None:
    im = Image.open(io.BytesIO(png)).convert('RGB')
else:  # the same pixels through ImageMagick
    import re
    class _Im:
        height = 240
        def __init__(self):
            fmt = ' '.join(f'%[pixel:p{{{x},{min(max(y + d, 0), 239)}}}]' for i in range(0, len(vals), 5)
                           for x, y in [vals[i:i + 2]] for d in (0, -1, 1))
            out = subprocess.run(['convert', 'png:-', '-format', fmt, 'info:'], input=png, capture_output=True).stdout.decode()
            cols = [tuple(int(v) for v in m) for m in re.findall(r'srgba?\((\d+),(\d+),(\d+)', out)]
            self.px = {}; k = 0
            for i in range(0, len(vals), 5):
                x, y = vals[i:i + 2]
                for d in (0, -1, 1):
                    self.px[(x, min(max(y + d, 0), 239))] = cols[k] if k < len(cols) else (-99, -99, -99); k += 1
        def getpixel(self, xy): return self.px.get(xy, (-99, -99, -99))
    im = _Im()
for i in range(0, len(vals), 5):
    x, y, r, g, b = vals[i:i + 5]
    ok = any(all(abs(a - c) <= 3 for a, c in zip(im.getpixel((x, min(max(y + d, 0), im.height - 1))), (r, g, b)))
             for d in (0, -1, 1))
    if not ok:
        sys.exit(1)
sys.exit(0)
