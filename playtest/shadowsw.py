# shadowsw.py [0|1]: DSCLOG's figures' shadows switch (shadows_on, its header +220) read, or set: 0 for
# a picture without shadows (docs/shadows.png's left half), 1 back. The shadows are always on in the
# mod (no switch in the Options tab), so this is the control. Memory only; scroll the view a pixel
# and back (scroll.py 1 0, -1 0) so the map is drawn again (logs/2026-11-27-outfit-screenshots.md).
import os, re, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]; sys.argv = sys.argv[:1]
exec(open(os.path.join(HERE, 'live.py')).read())
from dsloader import dicelog
mem = g.read(0, 0x110000)
hdr = next(m.start() for m in re.finditer(re.escape(dicelog.HDR_SIG), mem) if m.start() % 16 == 0)
if args:
    g.write(hdr + 220, struct.pack('<H', int(args[0])))
print('shadows_on', struct.unpack('<H', g.read(hdr + 220, 2))[0])
