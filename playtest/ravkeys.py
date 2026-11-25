"""ravkeys.py: R, F10 and Alt in the running sequel ($WORK/rav.pid): DSCLOG2's words for them and the game's.
  python3 ravkeys.py           one line: DSCLOG2's header +1922 to +1934 (VIEW_REDRAW, SQUARES_ON, LIGHT's offset, the
                               squares' floor passes, F10's moves taken back and refused, the rings drawn under
                               RING_TAB's marks), RINGS_ON, RING_TAB's marks (how many), whose turn, and for a party
                               member's turn its square, movement points (3C4Fh:22Eh), turn flags (+1D8h), swings and
                               attack commands (+184h, +1AEh), F10's turn start (DS:4258h points, 425Ch x, 425Ah y)
                               and SQ_MAP's marks (how many, in DSCLOG2's PSP)
  python3 ravkeys.py things    the game's draw list (DS:67B7h far, its count DS:264Eh, 8 bytes an entry): each
                               thing's kind and number (the things table, 3F49h:C33h), an item's type, name, contents
                               and the map record's object (+1Bh) and bytes +6 to +9; a creature's name, side, status
                               and id (+6)
  python3 ravkeys.py marks     usable.marks through the dice log's own reading (a RavDiceLog attached read-only):
                               what Alt would ring, and why
  python3 ravkeys.py effect OWNER EFFECT | del OWNER EFFECT   an untimed effect given to combatant OWNER in memory (the
                               sequel's table, the load + 3E71h:24Dh, its count DS:2100h, 10 bytes a record as
                               addeffect.py's), or taken out: a test edit, never saved (66 Cannot Move, 69 Paralyzed)"""
import argparse, os, struct, sys
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)
load = ds - ravager.DGROUP
w = lambda a: struct.unpack('<H', g.read(a, 2))[0]


def hdr():
    seg = w(0xF5 * 4 + 2)
    return seg * 16


def state():
    h = hdr()
    words = [w(h + o) for o in range(1922, 1936, 2)]
    far = w(h + 142) * 16
    tab = g.read(far + w(h + 246), 520) if w(h + 246) else b''
    turn = w(ds * 16 + 0x426D)
    out = ('redraw %d squares_on %d light %#x sq_draws %d f10_moves %d f10_kept %d mark_draws %d | rings_on %d '
           'marks %d ring_draws %d | turn %d' % (*words, w(h + 244), sum(1 for b in tab if b), w(h + 1882), turn))
    if turn < 4:
        c = struct.unpack('<BH', g.read((load + 0x3F49) * 16 + 0xC33 + turn * 3, 3))[1]
        seg = (load + 0x3C4F) * 16
        x, y = struct.unpack('<HH', g.read(ds * 16 + 0x67C5 + turn * 0x25, 4))
        out += (' creature %d square %d,%d points %d flags %#x swings %d commands %d start %d at %d,%d walking %d'
                % (c, x >> 4, y >> 4, struct.unpack('<h', g.read(seg + 0x22E + c * 2, 2))[0], w(seg + 0x1D8 + c * 2),
                   g.read(seg + 0x184 + c, 1)[0], g.read(seg + 0x1AE + c, 1)[0], w(ds * 16 + 0x4258),
                   w(ds * 16 + 0x425C) >> 4, w(ds * 16 + 0x425A) >> 4, g.read(ds * 16 + 0x67BB + turn * 0x25, 1)[0] & 0x20))
    sq = g.read(h - 0x100 + 0x5C, 130)
    out += ' | SQ_MAP at %d,%d, %d marked' % (sq[0], sq[1], sum(bin(b).count('1') for b in sq[2:]))
    print(out)


def things():
    count = w(ds * 16 + 0x264E)
    off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x67B7, 4))
    raw = g.read(seg * 16 + off, min(count, 2000) * 8)
    tt = g.read((load + 0x3F49) * 16 + 0xC33, 520 * 3)
    ioff, iseg = struct.unpack('<HH', g.read(ds * 16 + ravager.ITEMS_PTR, 4))
    coff, cseg = struct.unpack('<HH', g.read(ds * 16 + ravager.CREATURES_PTR, 4))
    cam = struct.unpack('<hh', g.read(ds * 16 + 0x1408, 4))
    print('draw list: %d, view %s' % (count, cam))
    for i in range(len(raw) // 8):
        x, y, a, b, thing = struct.unpack_from('<hhBBH', raw, i * 8)
        if thing >= 520:
            continue
        kind, idx = struct.unpack_from('<Bh', tt, thing * 3)
        rec = g.read(ds * 16 + 0x67BB + thing * 0x25, 0x25)
        line = 'thing %3d at %5d,%5d (%3d,%3d) kind %d #%d obj %d rec6-9 %s' % (
            thing, x, y, x - cam[0], y - cam[1], kind, idx, struct.unpack_from('<h', rec, 0x1B)[0], rec[6:10].hex())
        if kind == 1 and 0 <= idx < 400:
            it = g.read(iseg * 16 + ioff + idx * ravager.ITEM_SIZE, ravager.ITEM_SIZE)
            line += ' item id %d type %d name# %d contents %d' % (struct.unpack_from('<h', it, 0)[0],
                    struct.unpack_from('<H', it, 0x0A)[0], struct.unpack_from('<H', it, 0x14)[0], struct.unpack_from('<H', it, 8)[0])
        elif kind == 2 and 0 <= idx < 512:
            cr = g.read(cseg * 16 + coff + idx * ravager.CREATURE_SIZE, ravager.CREATURE_SIZE)
            line += ' creature %r side %d status %d id %d hp %d' % (cr[0x21:0x31].split(b'\0')[0].decode('latin1'),
                    cr[0x15], cr[0x14], struct.unpack_from('<h', cr, 6)[0], struct.unpack_from('<h', cr, 0)[0])
        print(line)


def marks():
    from dsloader import ravlog, usable
    log = ravlog.RavDiceLog(g)
    print(log.attach())
    for m in usable.marks(log.game):
        print(m)


def effect():
    base, cnt = (load + 0x3E71) * 16 + 0x24D, ds * 16 + 0x2100
    count = w(cnt)
    recs = [g.read(base + i * 10, 10) for i in range(count)]
    if sys.argv[2] == 'del':
        owner, eff = int(sys.argv[3]), int(sys.argv[4])
        keep = [r for r in recs if not (struct.unpack_from('<h', r)[0] == owner and r[6] == eff)]
        g.write(base, b''.join(keep) + bytes(10 * (count - len(keep))))
        g.write(cnt, struct.pack('<H', len(keep)))
        print('removed', count - len(keep))
        return
    owner, eff = int(sys.argv[2]), int(sys.argv[3])
    at = 0
    while at < count and struct.unpack_from('<h', recs[at])[0] <= owner:
        at += 1
    recs.insert(at, struct.pack('<hhhBBBB', owner, owner, 0, eff, 0, 0, 0))
    g.write(base, b''.join(recs))
    g.write(cnt, struct.pack('<H', count + 1))
    print('given: %d records' % (count + 1))


{'things': things, 'marks': marks, 'effect': effect}.get(sys.argv[1] if len(sys.argv) > 1 else '', state)()
