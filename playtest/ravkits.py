"""ravkits.py: the kits in the running sequel ($WORK/rav.pid; the Loader's 48h sheets at the far pointer DS:19C5h).
  python3 ravkits.py show                      each party member's race, classes, levels and kit byte (+3Dh)
  python3 ravkits.py set MEMBER BYTE [RACE [CLASS...]]  a test edit (never save after it): the kit byte (two
                                               bits a class place, as kitpages.kit_byte; 0 none), and the race
                                               and the classes (1-17, up to 3; the rest 0) if given
  python3 ravkits.py count                     DSCLOG2's kit counters (KITS: kit_acs, kit_hits ...) and its
                                               rules words, from a symbol map of obsidian-edition/dos/dsclog2.asm
MEMBER is the sheet's number (0-3: the party's order)."""
import argparse, os, struct, subprocess, sys, tempfile
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import ravager
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
DOS = os.path.join(PT, '..', 'obsidian-edition', 'dos')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
COUNTERS = ('kit_acs', 'kit_hits', 'kit_damages', 'kit_rates', 'kit_saves', 'kit_skills_n', 'kit_rears',
            'kit_moves', 'kit_twos', 'kit_inits', 'spec_hits', 'spec_damages', 'spec_rates')


def helper():
    """(the helper's base address, its symbols): the INT F5h vector's segment (DSCLOG2's SITE)."""
    seg = struct.unpack('<H', g.read(0xF5 * 4 + 2, 2))[0]
    with tempfile.TemporaryDirectory() as t:
        src, mp = os.path.join(t, 'm.asm'), os.path.join(t, 'm.map')
        with open(src, 'w') as f:
            f.write(f"[map symbols {mp}]\n" + open(os.path.join(DOS, 'dsclog2.asm')).read())
        subprocess.run(['nasm', '-f', 'bin', '-I', DOS + '/', '-o', os.path.join(t, 'm.exe'), src], check=True)
        listing = open(mp).read()
    sym = {}
    for line in listing.split('Section image')[1].split('---- Section')[0].splitlines():
        p = line.split()
        if len(p) == 3:
            try:
                sym[p[2]] = int(p[1], 16)
            except ValueError:
                pass
    return seg * 16, sym


def sheets_at():
    from dsloader import game
    ds = game.find_data_segment(g)
    off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x19C5, 4))
    return seg * 16 + off


cmd = sys.argv[1] if len(sys.argv) > 1 else 'show'
if cmd == 'show':
    base = sheets_at()
    for m in range(4):
        s = g.read(base + m * ravager.SHEET_SIZE, ravager.SHEET_SIZE)
        print(m, 'race', s[0x12], 'classes', list(s[0x1B:0x1E]), 'levels', list(s[0x1E:0x21]),
              'kit byte %#04x' % s[0x3D], 'base AC', struct.unpack('b', s[0x21:0x22])[0], 'specs', s[0x42:0x45].hex())
elif cmd == 'set':
    m, byte = int(sys.argv[2]), int(sys.argv[3], 0)
    at = sheets_at() + m * ravager.SHEET_SIZE
    g.write(at + 0x3D, bytes((byte,)))
    if len(sys.argv) > 4:
        g.write(at + 0x12, bytes((int(sys.argv[4]),)))
    if len(sys.argv) > 5:
        g.write(at + 0x1B, bytes(([int(c) for c in sys.argv[5:8]] + [0, 0, 0])[:3]))
    print('member', m, 'kit byte %#04x' % g.read(at + 0x3D, 1)[0], 'race', g.read(at + 0x12, 1)[0])
elif cmd == 'count':
    base, sym = helper()
    hdr = base + sym['hdr']
    print('rules %#06x rules_hi %#06x' % struct.unpack('<HH', g.read(hdr + 170, 2) + g.read(hdr + 270, 2)),
          'outdoors %#04x dance %s wild %#04x' % (g.read(hdr + 350, 1)[0], g.read(hdr + 351, 4).hex(), g.read(hdr + 355, 1)[0]))
    print(' '.join('%s=%d' % (n, struct.unpack('<H', g.read(base + sym[n], 2))[0]) for n in COUNTERS))
