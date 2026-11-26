"""ravspecs.py [MEMBER...|check]: the weapon specs of the running sequel's party and DSCLOG2's WEAPON PICKS' counts,
read only. ($WORK/rav.pid's DOSBox; the Loader's 48h sheets at the far pointer DS:19C5h, the specs at +42h..+44h:
game.specs_of; the counts wp_asks, wp_picked, wp_filled, lv_mode, lv_left, lv_avail.)
  python3 ravspecs.py [MEMBER...]   for each member (default 0-3): its name, race, classes, levels, kit byte, the
                                    specs' three bytes and their kinds by name (specialize.KINDS), the roll kept
  python3 ravspecs.py check         the build in memory: the first 40 bytes of WEAPON PICKS' routines against
                                    dos/DSCLOG2.EXE (by nasm's symbols), and DSCLOG2's rules word (header +170)
Run from playtest/."""
import argparse, os, struct, subprocess, sys, tempfile
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager, specialize
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
DOS = os.path.join(PT, '..', 'obsidian-edition', 'dos')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))


def helper():
    """(the helper's base address, its symbols): the INT F5h vector's segment (DSCLOG2's SITE), as ravkits.py."""
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


if sys.argv[1:] == ['check']:
    base, sym = helper()
    exe = open(os.path.join(DOS, 'DSCLOG2.EXE'), 'rb').read()
    img = exe[struct.unpack_from('<H', exe, 8)[0] * 16:]
    for n in ('cr_weapons', 'wp_ask', 'wp_kinds', 'lv_due', 'wp_fill', 'pk_win', 'pk_title', 'pk_fill', 'pk_click',
              'pk_hover', 'wp_take', 'pk_word', 'spec_set', 'spec_repack', 'psi_count', 'site_table'):
        print(n, 'same' if g.read(base + sym[n], 40) == img[sym[n]:sym[n] + 40] else 'DIFFERENT')
    print('rules %#06x' % struct.unpack('<H', g.read(base + sym['hdr'] + 170, 2)))
    sys.exit(0)
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x19C5, 4))
coff, cseg = struct.unpack('<HH', g.read(ds * 16 + 0x19C9, 4))
for m in [int(a) for a in sys.argv[1:]] or range(4):
    s = g.read(seg * 16 + off + m * ravager.SHEET_SIZE, ravager.SHEET_SIZE)
    name = g.read(cseg * 16 + coff + m * 0x31 + 0x21, 16).split(b'\0')[0].decode('latin-1')
    specs, roll = game.specs_of(s[0x42:0x46])
    kinds = [specialize.KINDS[k - 1] for k in specs if k]
    print(m, name or '-', 'race', s[0x12], 'classes', list(s[0x1B:0x1E]), 'levels', list(s[0x1E:0x21]),
          'kit %#04x' % s[0x3D], 'specs', s[0x42:0x46].hex(), kinds, 'roll', roll)
base, sym = helper()
words = {n: struct.unpack('<H', g.read(base + sym[n], 2))[0] for n in ('wp_asks', 'wp_picked', 'wp_filled')}
print(' '.join('%s=%d' % kv for kv in words.items()), 'lv_mode=%d lv_left=%d lv_avail=%#x' % (
    g.read(base + sym['lv_mode'], 1)[0], g.read(base + sym['lv_left'], 1)[0],
    struct.unpack('<I', g.read(base + sym['lv_avail'], 4))[0]))
