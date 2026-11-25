"""ravquick.py: the quick saves in the running sequel ($WORK/rav.pid): DSCLOG2's QUICK SAVES (its header's +1904 on,
MAIN_TICKS at +260) and the game's words the Loader writes for them.
  python3 ravquick.py            the two keys (FFFF: the game's), their counts, SAVE_REQ (3 done, 4 failed, 5 a fight),
                                 SAVE_GREQ, the GREQ chunks written and read, the saves and loads made, MAIN_TICKS,
                                 SAVE_TEXT's file and name, the page letter (DS:2088h, 20B9h), the window's chosen row
                                 (2F8h:0, the load + 3C4Ch), the map's limits (DS:14D7h-14DEh) and the screen word (0DABh)
  python3 ravquick.py greq FOLDER  the GREQ chunks of FOLDER's CHARSAVE.GFF (the map's limits each save keeps there)"""
import argparse, os, struct, sys
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader import gff, ravager, ravlog

if len(sys.argv) > 2 and sys.argv[1] == 'greq':
    chunks = gff.read_gff(open(os.path.join(sys.argv[2], 'CHARSAVE.GFF'), 'rb').read())
    for (kind, n), data in sorted(chunks.items()):
        if kind == 'GREQ':
            print('GREQ %d: limits %s, byte %d' % (n, struct.unpack_from('<4H', data), data[8] if len(data) > 8 else -1))
    sys.exit()

from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
seg = struct.unpack('<H', g.read(0xF5 * 4 + 2, 2))[0]
low = g.read(seg * 16, 0x10000)
hdr = seg * 16 + low.find(b'DSCLOGR1')
w = lambda at, n=1: struct.unpack('<%dH' % n, g.read(at, 2 * n))
L = ravlog.QUICK_LAYOUT
print('keys %04X %04X  seq %d %d  req %d  greq %d  greq written %d read %d  main_ticks %d' % (
    *w(hdr + L.keys, 2), *w(hdr + L.seq, 2), *w(hdr + L.req), *w(hdr + L.greq), *w(hdr + ravlog.QUICK_GREQ_SAVES),
    *w(hdr + ravlog.QUICK_GREQ_LOADS), *w(hdr + L.main_ticks)))
text = g.read(w(hdr + L.tail_seg)[0] * 16 + w(hdr + L.save_off)[0], 112)
print('SAVE_TEXT %r %r' % (text[:64].split(b'\0')[0], text[64:].split(b'\0')[0]))
ravlog.apply_layout()
ds = game.find_data_segment(g)
if ds is not None:
    print('letters %r %r  chosen %d  limits %s byte %d  screen %d' % (
        g.read(ds * 16 + L.name_find, 1), g.read(ds * 16 + L.name_save, 1),
        w((ds - L.window_from_ds) * 16 + L.chosen)[0], w(ds * 16 + 0x14D7, 4), g.read(ds * 16 + 0x4459, 1)[0],
        w(ds * 16 + L.screen_is)[0]))
