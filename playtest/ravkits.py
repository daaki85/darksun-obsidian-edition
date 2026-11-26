"""ravkits.py: the kits in the running sequel ($WORK/rav.pid; the Loader's 48h sheets at the far pointer DS:19C5h).
  python3 ravkits.py show                      each party member's race, classes, levels and kit byte (+3Dh)
  python3 ravkits.py set MEMBER BYTE [RACE [CLASS...]]  a test edit (never save after it): the kit byte (two
                                               bits a class place, as kitpages.kit_byte; 0 none), and the race
                                               and the classes (1-17, up to 3; the rest 0) if given
  python3 ravkits.py count                     DSCLOG2's kit counters (KITS: kit_acs, kit_hits ...; the two
                                               weapons' two_count, off_count, rg_heavy too) and its
                                               rules words, from a symbol map of obsidian-edition/dos/dsclog2.asm
  python3 ravkits.py match C1,C2 BYTE [RACE [CLASS...]]  set (as set) the member whose classes are C1,C2 (any order;
                                               c, d, r: any cleric, druid, ranger)
  python3 ravkits.py flags MEMBER [WORD]       the sheet's flags word (+10h, SL's +12h: 200h a ranger, as the two-weapon
                                               routine's test reads it), and with WORD a test edit setting it (+WORD: those bits added)
  python3 ravkits.py levels MEMBER L1 [L2 L3]  a test edit: the class levels (+1Eh..+20h; the rest 0)
  python3 ravkits.py sphere MEMBER N           a test edit: an Elementalist's second sphere (+3Fh's low three bits:
                                               0 none, 1 air, 2 earth, 3 fire, 4 water), the bits above kept
  python3 ravkits.py hp MEMBER N               a test edit: the creature's hit points (+0) N, and its sheet's most
  python3 ravkits.py page                      the creation screen's KIT pages (DSCLOG2's KIT PAGE): the sheet being
                                               made (far DS:1429h: race, classes, kit byte), the panel's windows
                                               (DS:1134h, 1138h: their ids), the pages shown and rows taken
  python3 ravkits.py power MEMBER POWER [BYTE]  a test edit: the member's own byte for psionic power POWER (0-33, the
                                               sequel's spells EBh on: 31 Psionic Blast) at selector 370h (the load +
                                               3E71h):9CDh + member x 22h (SL's 2F0h:77h), BYTE (default 0Ah: bit 1 and
                                               an own number of 1, bits 3-7), and its PSP (+2, and the sheet's most) 200
  python3 ravkits.py blast                     DSCLOG2's Psionic Blast words (BLAST_HP, +1814: each member's hit points
                                               owed), its counts (blast_seen, blast_kos) and the creation's RL_SEQ and
                                               RL_TRIES (+280, +282), and the party's HP and status (+14h)
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
            'kit_moves', 'kit_twos', 'kit_inits', 'kit_stabs', 'stabs', 'enlarges', 'el_spheres', 'spec_hits',
            'spec_damages', 'spec_rates', 'two_count', 'off_count', 'rg_heavy', 'blast_seen', 'blast_kos')


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
              'kit byte %#04x' % s[0x3D], 'sphere byte %#04x' % s[0x3F], 'base AC', struct.unpack('b', s[0x21:0x22])[0], 'flags %#06x' % struct.unpack_from('<H', s, 0x10), 'specs', s[0x42:0x45].hex())
elif cmd in ('set', 'match'):
    m, byte = int(sys.argv[2]) if cmd == 'set' else None, int(sys.argv[3], 0)
    if m is None:
        groups = {'c': range(1, 5), 'd': range(5, 9), 'r': range(13, 17)}  # (any cleric, druid, ranger)
        want = [groups.get(c, None) or (int(c),) for c in sys.argv[2].split(',')]

        def fits(classes):
            return len(classes) == len(want) and all(any(c in w for c in classes) for w in want)
        m = next(n for n in range(4) if fits([c for c in g.read(sheets_at() + n * ravager.SHEET_SIZE + 0x1B, 3) if c]))
    at = sheets_at() + m * ravager.SHEET_SIZE
    g.write(at + 0x3D, bytes((byte,)))
    if len(sys.argv) > 4 and sys.argv[4] != '-':  # ('-': the race kept)
        g.write(at + 0x12, bytes((int(sys.argv[4]),)))
    if len(sys.argv) > 5:
        g.write(at + 0x1B, bytes(([int(c) for c in sys.argv[5:8]] + [0, 0, 0])[:3]))
    print('member', m, 'kit byte %#04x' % g.read(at + 0x3D, 1)[0], 'race', g.read(at + 0x12, 1)[0])
elif cmd == 'flags':
    m, at = int(sys.argv[2]), sheets_at() + int(sys.argv[2]) * ravager.SHEET_SIZE + 0x10
    if len(sys.argv) > 3:
        old, = struct.unpack('<H', g.read(at, 2))
        word = old | int(sys.argv[3][1:], 0) if sys.argv[3].startswith('+') else int(sys.argv[3], 0)
        g.write(at, struct.pack('<H', word))
        print(m, 'was %#06x' % old)
    print(m, 'flags %#06x' % struct.unpack('<H', g.read(at, 2)), '(200h a ranger)')
elif cmd == 'levels':
    at = sheets_at() + int(sys.argv[2]) * ravager.SHEET_SIZE
    g.write(at + 0x1E, bytes(([int(n) for n in sys.argv[3:6]] + [0, 0, 0])[:3]))
    print('member', sys.argv[2], 'levels', list(g.read(at + 0x1E, 3)))
elif cmd == 'sphere':
    at = sheets_at() + int(sys.argv[2]) * ravager.SHEET_SIZE + 0x3F
    g.write(at, bytes((g.read(at, 1)[0] & 0xF8 | int(sys.argv[3]),)))
    print('member', sys.argv[2], 'sphere byte %#04x' % g.read(at, 1)[0])
elif cmd == 'hp':
    from dsloader import game
    ds = game.find_data_segment(g)
    off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x19C9, 4))
    m, n = int(sys.argv[2]), int(sys.argv[3])
    cr = seg * 16 + off + m * 0x31
    sheet = sheets_at() + struct.unpack('<H', g.read(cr + 4, 2))[0] * ravager.SHEET_SIZE
    g.write(sheet + 8, struct.pack('<H', n))
    g.write(cr, struct.pack('<H', n))
    print('member', m, 'hp', struct.unpack('<H', g.read(cr, 2))[0])
elif cmd == 'page':
    from dsloader import game
    ds = game.find_data_segment(g)
    off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x1429, 4))
    s = g.read(seg * 16 + off, 0x42)
    print('creation sheet %04X:%04X race %d classes %s kit byte %#04x editing %d' % (
        seg, off, s[0x12], list(s[0x1B:0x1E]), s[0x3D], struct.unpack('<h', g.read(ds * 16 + 0x112E, 2))[0]))
    for name, at in (('disciplines', 0x1134), ('spheres/page', 0x1138)):
        o, sg = struct.unpack('<HH', g.read(ds * 16 + at, 4))
        print(name, 'none' if not (o or sg) else 'window %d' % struct.unpack('<H', g.read(sg * 16 + o + 8, 2))[0])
    print('marks: disciplines %#x spheres %#x' % struct.unpack('<HH', g.read(ds * 16 + 0x42C0, 4)))
    base, sym = helper()
    print('rules_hi %#06x' % struct.unpack('<H', g.read(base + sym['hdr'] + 270, 2)),
          ' '.join('%s=%d' % (n, struct.unpack('<H', g.read(base + sym[n], 2))[0]) for n in ('kit_pages_shown', 'kit_rows_taken', 'dual_asks', 'dual_kits')),
          'seen %08x keep %d first %d' % (struct.unpack('<I', g.read(base + sym['wp_classes_seen'], 4))[0],
                                          g.read(base + sym['kit_keep'], 1)[0], g.read(base + sym['kp_first'], 1)[0]))
elif cmd == 'power':
    from dsloader import game
    ds = game.find_data_segment(g)
    member, power = int(sys.argv[2]), int(sys.argv[3])
    value = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0x0A
    at = (ds - ravager.DGROUP + 0x3E71) * 16 + 0x9CD + member * 0x22
    print('powers before', g.read(at, 34).hex())
    g.write(at + power, bytes((value,)))
    off, seg = struct.unpack('<HH', g.read(ds * 16 + ravager.CREATURES_PTR, 4))
    g.write(seg * 16 + off + member * ravager.CREATURE_SIZE + 2, struct.pack('<h', 200))
    print('powers after ', g.read(at, 34).hex(), 'PSP 200')
elif cmd == 'blast':
    from dsloader import game
    ds = game.find_data_segment(g)
    base, sym = helper()
    hdr = base + sym['hdr']
    print('BLAST_HP', struct.unpack('<4h', g.read(hdr + 1814, 8)),
          ' '.join('%s=%d' % (n, struct.unpack('<H', g.read(base + sym[n], 2))[0]) for n in ('blast_seen', 'blast_kos')),
          'RL_SEQ', struct.unpack('<H', g.read(hdr + 280, 2))[0], 'RL_TRIES', list(g.read(hdr + 282, 24)))
    off, seg = struct.unpack('<HH', g.read(ds * 16 + ravager.CREATURES_PTR, 4))
    for m in range(4):
        r = g.read(seg * 16 + off + m * ravager.CREATURE_SIZE, ravager.CREATURE_SIZE)
        print('member', m, 'HP', struct.unpack_from('<h', r, 0)[0], 'PSP', struct.unpack_from('<h', r, 2)[0], 'status', r[0x14])
elif cmd == 'count':
    base, sym = helper()
    hdr = base + sym['hdr']
    print('rules %#06x rules_hi %#06x' % struct.unpack('<HH', g.read(hdr + 170, 2) + g.read(hdr + 270, 2)),
          'outdoors %#04x dance %s wild %#04x' % (g.read(hdr + 350, 1)[0], g.read(hdr + 351, 4).hex(), g.read(hdr + 355, 1)[0]))
    print(' '.join('%s=%d' % (n, struct.unpack('<H', g.read(base + sym[n], 2))[0]) for n in COUNTERS))
