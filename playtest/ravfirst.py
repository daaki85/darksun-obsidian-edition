"""ravfirst.py: a sequel party member's wizard spells and psionic powers as the game holds them, and DSCLOG2's
first spells' and powers' counts (the running sequel, $WORK/rav.pid; read only).
  python3 ravfirst.py [MEMBER...]   for each member (default 0-3): its sheet's classes and levels, the wizard
                                    spells known (selector 320h, the load + 3D62h: 39Ch + 15 a member, bit n spell
                                    n) by level and name, the powers known (selector 370h, the load + 3E71h: 9CDh +
                                    22h a member, bits 1-7 the power's number) and the disciplines' bits (A55h +
                                    the member); then DSCLOG2's CR_PICKS/PSI_GRANT counts (cr_members, cr_windows,
                                    cr_picked, cr_filled, psi_asks, psi_filled, psi_kept) and its psi_due, cr_cap
Run from playtest/."""
import argparse, os, struct, subprocess, sys, tempfile
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager, ravlog
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
DOS = os.path.join(PT, '..', 'obsidian-edition', 'dos')
g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
args = sys.argv[1:]


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


ds = game.find_data_segment(g)
load = ds - ravager.DGROUP
STARTS = list(g.read(ds * 16 + 0x656, 11))
names = ravlog.spell_table(open(ravlog.resources_file() or os.path.join(os.environ.get('RAV', '/tmp/playtest/rav'), 'RESOURCE.GFF'), 'rb').read())[1]
off, seg = struct.unpack('<HH', g.read(ds * 16 + 0x19C5, 4))
base = seg * 16 + off
for m in [int(a) for a in args] or range(4):
    s = g.read(base + m * ravager.SHEET_SIZE, ravager.SHEET_SIZE)
    bits = g.read((load + 0x3D62) * 16 + 0x39C + 15 * m, 15)
    known = [n for n in range(STARTS[10]) if bits[n // 8] >> (n % 8) & 1]
    by = {}
    for n in known:
        by.setdefault(next(lv for lv in range(1, 11) if n < STARTS[lv]), []).append(names[n])
    pw = g.read((load + 0x3E71) * 16 + 0x9CD + 0x22 * m, 34)
    disc = g.read((load + 0x3E71) * 16 + 0xA55 + m, 1)[0]
    print(f"member {m}: classes {list(s[0x1B:0x1E])} levels {list(s[0x1E:0x21])}")
    print(f"  wizard spells ({len(known)}):", '; '.join(f"L{lv} " + ', '.join(v) for lv, v in sorted(by.items())))
    print(f"  powers ({sum(1 for b in pw if b >> 1)}), disciplines {disc & 7:03b}:",
          ', '.join(f"{names[0xEB + p]}" + (f" ({pw[p] >> 1})" if pw[p] >> 1 != 1 else '') for p in range(34) if pw[p] >> 1))
at, sym = helper()
words = ('cr_members', 'cr_windows', 'cr_picked', 'cr_filled', 'psi_asks', 'psi_filled', 'psi_kept')
print('DSCLOG2:', ' '.join(f"{w}={struct.unpack('<H', g.read(at + sym[w], 2))[0]}" for w in words),
      f"psi_due={g.read(at + sym['psi_due'], 1)[0]} cr_cap={g.read(at + sym['cr_cap'], 1)[0]}")
