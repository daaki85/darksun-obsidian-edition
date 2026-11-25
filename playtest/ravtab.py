"""ravtab.py: the state of choosing an enemy with Tab in the running sequel ($WORK/rav.pid; DSCLOG2's TARGETING and
RINGS, from a symbol map of obsidian-edition/dos/dsclog2.asm, as ravkits.py count).
  python3 ravtab.py            one line: DSCLOG2's words (rings_on, target_on, the Tab, Shift+Tab and Enter counts,
                               hit_target, the clicks given, the finder's forced answers, the rings drawn, the main
                               loop's passes) and the game's (whose turn, the pointer's mode at DS:1440h, the thing
                               under the pointer DS:0DADh, the pointer DS:A109h)
  python3 ravtab.py feet       each combatant's map thing's feet (DS:67BBh + 25h x thing, +0Ah, +0Ch) and the view
                               (DS:1408h), the screen place of each (window x = game x x 2, y x 2.4 at 640x480)"""
import argparse, os, struct, subprocess, sys, tempfile
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
DOS = os.path.join(PT, '..', 'obsidian-edition', 'dos')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
HEADER = (('rings_on', 244), ('target_on', 250), ('tab_seq', 252), ('back_seq', 254), ('hit_target', 256),
          ('attack_seq', 258), ('attack_clicks', 1878), ('hit_answers', 1880), ('ring_draws', 1882))


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


def word(at):
    return struct.unpack('<H', g.read(at, 2))[0]


ds = game.find_data_segment(g) * 16
cmd = sys.argv[1] if len(sys.argv) > 1 else 'state'
if cmd == 'feet':
    cx, cy = struct.unpack('<hh', g.read(ds + 0x1408, 4))
    print('view %d,%d' % (cx, cy))
    seg, off = 0x3F49, 0xC33  # (the fight's combatants, ravlog's COMBATANTS_SEG/OFF)
    load = ds // 16 - ravager.DGROUP
    for n in range(40):
        kind, index = struct.unpack('<BH', g.read((load + seg) * 16 + off + 3 * n, 3))
        if kind == 0 and index == 0 and n:
            continue
        x, y = struct.unpack('<hh', g.read(ds + 0x67BB + 0x25 * n + 0x0A, 4))
        if x or y:
            print('thing %2d kind %d creature %3d feet %4d,%4d screen %4d,%4d' % (n, kind, index, x, y, x - cx, y - cy))
else:
    base, sym = helper()
    hdr = base + sym['hdr']
    print(' '.join('%s=%#x' % (n, word(hdr + o)) if n == 'hit_target' else '%s=%d' % (n, word(hdr + o))
                   for n, o in HEADER),
          'main_ticks=%d' % word(base + sym['main_ticks']),
          'turn=%d mode=%d under=%#x pointer=%d,%d' % (word(ds + ravager.WHOSE_TURN), word(ds + 0x1440),
                                                      word(ds + 0x0DAD), *struct.unpack('<hh', g.read(ds + 0xA109, 4))))
