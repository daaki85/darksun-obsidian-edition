"""ravlevel.py: the level cap by XP in the running sequel ($WORK/rav.pid; the Loader's 48h sheets at the far pointer DS:19C5h).
  python3 ravlevel.py show                     each member's race, classes, levels, best levels (+39h), XP (+0), hit points
                                               (+8 the most, +0Ah the base), the five saves (+31h) and the creature's THAC0
                                               (+16h, signed), its casts left (DS:446Ah + 22h a member: a wizard's by spell level from
                                               +0, a priest's from +0Bh); then DSCLOG2's counters (lv_rooms, lv_tops, hd_tens, save_count, xp_pasts, xp_holds,
                                               slot_count) and its rules words
  python3 ravlevel.py set MEMBER XP RACE C1,C2,C3 L1,L2,L3   a test edit (never save after it): the XP, race, classes
                                               (1-17) and levels, the best levels (+39h) the same, so each new level
                                               is a new one (its hit die, its extras)
  python3 ravlevel.py powers MEMBER [all]     the member's psionic powers known (selector 370h's +9CDh, 22h a member,
                                               bit 1 known, 34 powers); "all" marks them all known, a test edit
  python3 ravlevel.py foes HP                  every foe's (creature +15h 7) hit points HP, a test edit
MEMBER is the sheet's number (0-3: the party's order)."""
import argparse, os, struct, subprocess, sys, tempfile
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
ds = game.find_data_segment(g)


def far(at):
    off, seg = struct.unpack('<HH', g.read(ds * 16 + at, 4))
    return seg * 16 + off


def helper():
    """(the helper's base address, its symbols): the INT F5h vector's segment (as ravkits.py's)."""
    seg = struct.unpack('<H', g.read(0xF5 * 4 + 2, 2))[0]
    dos = os.path.join(PT, '..', 'obsidian-edition', 'dos')
    with tempfile.TemporaryDirectory() as t:
        src, mp = os.path.join(t, 'm.asm'), os.path.join(t, 'm.map')
        with open(src, 'w') as f:
            f.write(f"[map symbols {mp}]\n" + open(os.path.join(dos, 'dsclog2.asm')).read())
        subprocess.run(['nasm', '-f', 'bin', '-I', dos + '/', '-o', os.path.join(t, 'm.exe'), src], check=True)
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


def sheet(m):
    return far(0x19C5) + m * ravager.SHEET_SIZE


cmd = sys.argv[1] if len(sys.argv) > 1 else 'show'
if cmd == 'show':
    for m in range(4):
        s = g.read(sheet(m), ravager.SHEET_SIZE)
        cr = g.read(far(0x19C9) + m * 0x31, 0x31)
        print(m, 'race', s[0x12], 'classes', list(s[0x1B:0x1E]), 'levels', list(s[0x1E:0x21]), 'best',
              list(s[0x39:0x3C]), 'XP', struct.unpack_from('<I', s, 0)[0], 'HP most', struct.unpack_from('<h', s, 8)[0],
              'base', struct.unpack_from('<h', s, 0x0A)[0], 'saves', list(s[0x31:0x36]), 'THAC0',
              struct.unpack_from('<b', cr, 0x16)[0], 'casts left', list(g.read(ds * 16 + 0x446A + m * 0x22, 0x22)))
    base, sym = helper()
    print('helper', ', '.join('%s %d' % (n, struct.unpack('<H', g.read(base + sym[n], 2))[0])
                              for n in ('lv_rooms', 'lv_tops', 'hd_tens', 'save_count', 'slot_count', 'xp_count', 'xp_pasts', 'xp_holds')),
          'rules %#06x rules_hi %#06x' % struct.unpack('<HH', g.read(base + sym['rules'], 2) + g.read(base + sym['rules_hi'], 2)))
elif cmd == 'set':
    m, xp, race = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    classes = [int(c) for c in sys.argv[5].split(',')] + [0, 0, 0]
    levels = [int(c) for c in sys.argv[6].split(',')] + [0, 0, 0]
    at = sheet(m)
    g.write(at, struct.pack('<I', xp))
    g.write(at + 0x12, bytes((race,)))
    g.write(at + 0x1B, bytes(classes[:3]))
    g.write(at + 0x1E, bytes(levels[:3]))
    g.write(at + 0x39, bytes(levels[:3]))
    s = g.read(at, 0x40)
    print('member', m, 'XP', struct.unpack_from('<I', s, 0)[0], 'race', s[0x12], 'classes', list(s[0x1B:0x1E]),
          'levels', list(s[0x1E:0x21]))
elif cmd == 'foes':
    n = int(sys.argv[2])
    base = far(0x19C9)
    for i in range(255):
        cr = base + i * 0x31
        if g.read(cr + 0x15, 1)[0] == 7 and struct.unpack('<h', g.read(cr, 2))[0] > 0:
            g.write(cr, struct.pack('<H', n))
            print('foe', i, 'HP', n)
elif cmd == 'powers':
    m = int(sys.argv[2])
    at = (ds + 0x3E71 - 0x47E0) * 16 + 0x9CD + m * 0x22   # (DSCLOG2's POW_SEG:POW_OFF, POW_SIZE a member)
    if len(sys.argv) > 3 and sys.argv[3] == 'all':
        g.write(at, bytes(b | 2 for b in g.read(at, 34)))
    p = g.read(at, 34)
    print('member', m, 'powers known', sum(1 for b in p if b & 2), 'of 34:', [i for i, b in enumerate(p) if b & 2])
