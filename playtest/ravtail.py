"""ravtail.py: DSCLOG2's parts in the running sequel ($WORK/rav.pid): its segment (the INT F5h vector's), the tail's
segment the helper set at its header's +1834 (it must be the segment + TAIL_PARAS, +1836) and the tail's signature
there, the tail's tables compared with the built dos/DSCLOG2.EXE's (SITE_TABLE, NS_CMP_TABLE, RAV_SLOTS, LARGE_DICE,
RAV_XP: section tail, which nothing writes), and the start of the Loader's buffers in it (SLOTS_TEXT, the item names,
LBL_SLOTS, LOOK_FULL), so a look at the USE screen can be matched with what the Loader wrote.
  python3 ravtail.py           all of it; exit status 1 if the tail's segment, signature or tables are wrong"""
import argparse, os, struct, subprocess, sys, tempfile
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
WORK = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
DOS = os.path.join(PT, '..', 'obsidian-edition', 'dos')
TABLES = ('site_table', 'ns_cmp_table', 'rav_slots', 'large_dice', 'rav_xp', 'tail_mid')
BUFFERS = (('slots_text', 128 * 4), ('item_names', 16 * 8), ('lbl_slots', 32), ('look_full', 64))


def symbols():
    """The built helper's sections' labels ({section: {label: offset}}) and its EQUs, from nasm's map."""
    with tempfile.TemporaryDirectory() as t:
        src, mp, exe = (os.path.join(t, n) for n in ('m.asm', 'm.map', 'm.exe'))
        with open(src, 'w') as f:
            f.write(f"[map symbols {mp}]\n" + open(os.path.join(DOS, 'dsclog2.asm')).read())
        subprocess.run(['nasm', '-f', 'bin', '-I', DOS + '/', '-o', exe, src], check=True)
        listing, image = open(mp).read(), open(exe, 'rb').read()[32:]
    out, equs = {}, {}
    for block in listing.split('---- Section ')[1:]:
        for line in block.splitlines()[1:]:
            p = line.split()
            if len(p) == 3 and all(c in '0123456789ABCDEF' for c in p[1]):
                out.setdefault(block.split()[0], {})[p[2]] = int(p[1], 16)
    for line in listing.split('No Section')[1].split('---- Section')[0].splitlines():
        p = line.split()
        if len(p) == 2 and all(c in '0123456789ABCDEF' for c in p[0]):
            equs[p[1]] = int(p[0], 16)
    return out, equs, image


def main():
    g = connect(argparse.Namespace(pid=int(open(os.path.join(WORK, 'rav.pid')).read()), host_base=None))
    sym, equs, image = symbols()
    seg = struct.unpack('<H', g.read(0xF5 * 4 + 2, 2))[0]
    hdr = seg * 16
    sig = g.read(hdr, 8)
    tail_seg, tail_paras = struct.unpack('<HH', g.read(hdr + 1834, 4))
    print(f'helper segment {seg:04X}h ({sig!r}), tail_seg {tail_seg:04X}h, tail_paras {tail_paras:X}h '
          f'(built: {equs["TAIL_PARAS"]:X}h, tail {equs["TAIL_LEN"] * 16} bytes, kept {(0x10 + equs["KEPT_PARAS"]) * 16} '
          f'with the PSP)')
    bad = sig != b'DSCLOGR1' or tail_seg != seg + tail_paras or tail_paras != equs['TAIL_PARAS']
    tail = tail_seg * 16
    print('tail signature:', g.read(tail, 12), '' if g.read(tail, 12) == b'DSCLOG2 TAIL' else ' WRONG')
    bad |= g.read(tail, 12) != b'DSCLOG2 TAIL'
    built = image[equs['TAIL_PARAS'] * 16:]
    t = sym['tail']
    for a, b in zip(TABLES, TABLES[1:]):
        same = g.read(tail + t[a], t[b] - t[a]) == built[t[a]:t[b]]
        bad |= not same
        print(f'  {a:13} +{t[a]:04X}h {t[b] - t[a]:5} bytes: {"as built" if same else "DIFFERENT"}')
    z = {**sym['tail'], **sym['tailz']}  # (the item names first in the tail, the rest after its tables)
    for name, n in BUFFERS:
        data = g.read(tail + z[name], n)
        text = data.split(b'\0' * 4)[0][:120]
        print(f'  {name:13} +{z[name]:04X}h: {text!r}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
