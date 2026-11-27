# ravaudit.py: DSCLOG2's words of the port audit's rest in the running sequel ($WORK/rav.pid): LOCK_BARRED (the
# tail's, its offset at the header's +2114: the locks each member failed at its thief level now, as the Loader
# wrote them), the open locks checks LOCK_SITE put out of reach (+2116), the gladiators' AC worked out with no
# armour (GL_ARMOUR, +2118), the computer's walls across the line of fire (AI_WALL, +2120), a party
# thri-kreen's natural attacks made edged (KREEN_CLAWS, +2122), Berserks put on with their side kept and ended with it
# given back (BERSERK_ADD, +2124; BERSERK_END, +2126), the header's length (HDR_LEN, +30), and the region and the thing the running script was started on. Run from playtest/.
import argparse, os, struct, sys
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
seg = struct.unpack('<H', g.read(0xF5 * 4 + 2, 2))[0]
hdr = None
for off in range(0, 0x400, 2):  # (the header: its signature DSCLOGR1)
    if g.read(seg * 16 + off, 8) == b'DSCLOGR1':
        hdr = seg * 16 + off; break
if hdr is None:
    sys.exit('no DSCLOG2 header at the INT F5h segment %04x' % seg)
w = lambda at: struct.unpack('<H', g.read(hdr + at, 2))[0]
tail = w(1834)
print('lock_off %04x lock_bars %d gl_bare %d ai_walls %d kreen_cuts %d berserk_sides %d berserk_ends %d hdr_len %d'
      % (w(2114), w(2116), w(2118), w(2120), w(2122), w(2124), w(2126), w(30)))
if tail and w(2114):
    rows = struct.unpack('<32H', g.read(tail * 16 + w(2114), 64))
    for m in range(4):
        print('member', m, ['(%d, %d)' % rows[m * 8 + 2 * i:m * 8 + 2 * i + 2] for i in range(4) if rows[m * 8 + 2 * i] != 0xFFFF])
ds = game.find_data_segment(g)
print('region %#x talk thing %d' % (struct.unpack('<H', g.read(ds * 16 + 0x140C, 2))[0],
                                     struct.unpack('<h', g.read((ds - 0x47E0 + 0x3C13) * 16 + 0x365, 2))[0]))
