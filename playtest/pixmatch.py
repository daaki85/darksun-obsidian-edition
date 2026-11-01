# pixmatch.py X Y R G B [X Y R G B ...]: exit 0 if every named pixel of a fresh 320x240 window
# grab is that colour, within 3 a channel and one row up or down. The tolerance is for the
# recompiled program (PT_TARGET=recomp): its VGA colours differ from DOSBox's by one (38 of 63
# is 153 there, 154 in DOSBox) and its 320x200 picture is scaled to the 240 rows a row apart.
import sys, os, subprocess, io
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from paths import WORK  # noqa (sets DISPLAY)
from PIL import Image
winq = os.environ.get('WINQ', '--class dosbox').split()
w = subprocess.run(['timeout', '5', 'xdotool', 'search'] + winq, capture_output=True, text=True).stdout.split()
if not w:
    print('no window'); sys.exit(2)
png = subprocess.run(['timeout', '10', 'import', '-window', w[0], 'png:-'], capture_output=True).stdout
im = Image.open(io.BytesIO(png)).convert('RGB')
vals = [int(v) for v in sys.argv[1:]]
for i in range(0, len(vals), 5):
    x, y, r, g, b = vals[i:i + 5]
    ok = any(all(abs(a - c) <= 3 for a, c in zip(im.getpixel((x, min(max(y + d, 0), im.height - 1))), (r, g, b)))
             for d in (0, -1, 1))
    if not ok:
        sys.exit(1)
sys.exit(0)
