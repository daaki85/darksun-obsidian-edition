# ravtext.py [N]: Wake of the Ravager's text buffer (DSCLOG2's TEXT, sites 93 and 94): the last N records (default
# 40) the dialogue window's input and the message box left in it (kind 0 a reply, 1 a portrait and its
# number, 2 text, 3 the replies shown, 16 a message box), the header's TPOS (+126; 0 with the probes left out),
# and who the game's script was started on (the load + 3C13h:365h, ravlog's TALK_SEG/TALK_TARGET).
import sys, os, struct, argparse
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, textlog
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
low = g.read(0, game.CONVENTIONAL_AND_UPPER)
hdr = low.find(b'DSCLOGR1')
while hdr % 16:
    hdr = low.find(b'DSCLOGR1', hdr + 1)
tpos, off, size, _, _, _, seg = struct.unpack_from('<7H', low, hdr + 126)
print('TPOS %d, buffer %04X:%04X (%d bytes)' % (tpos, seg, off, size))
if not seg:
    sys.exit('no text buffer (a DSCLOG2 before TEXT)')
buf = textlog.TextBuffer(g.read, hdr)
n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
buf.pos = (tpos - min(tpos, size)) & 0xFFFF  # (from the oldest the buffer still holds, if it wrapped: may start mid-record)
for rec in buf.poll()[-n:]:
    print('%2d %5d %s' % (rec.kind, rec.value, rec.text[:100]))
ds = game.find_data_segment(g, low)
load = ds - 0x47E0
print('talked to (thing):', struct.unpack('<h', g.read((load + 0x3C13) * 16 + 0x365, 2))[0])
