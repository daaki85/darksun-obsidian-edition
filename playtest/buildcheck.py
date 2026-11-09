# buildcheck.py [NAME...]: is the DSCLOG running in DOSBox the build in obsidian-edition/dos? Compares
# 40 bytes of each routine named (default: a set touched by the 2026-11-09 memory pass) in memory with
# dos/DSCLOG.EXE, checks every vector of the install's table (ALL_VECTORS) in segment 0 points at its
# handler, and the tail (TAIL_SEG, the header's +1834) against the EXE's tail: its segment, and its
# data that starts with values (the item types, the names), byte for byte. Read-only.
import sys, os, struct, subprocess, tempfile
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT); __file__ = os.path.join(PT, 'live.py')
exec(open(__file__).read())
DOS = os.path.join(os.path.dirname(PT), 'obsidian-edition', 'dos')
CHECK = ('rl_sites', 'site_tab', 'ring_points', 'ring_dot', 'ring_outer', 'label_tick', 'label_stamp',
         'label_put', 'probe_names_fill', 'probe_types_fill', 'probe_tick', 'dust_tick', 'puff_raise',
         'puff_draw', 'dust_pass', 'spans_flush', 'build_dark', 'dos_quit')  # (not the install's code: AFTER_INSTALL's buffers are over it)


def symbols():
    """{name: (section, offset)} from a symbol map of dsclog.asm as built."""
    with tempfile.TemporaryDirectory() as tmp:
        src, out, mp = (os.path.join(tmp, n) for n in ('m.asm', 'm.bin', 'm.map'))
        open(src, 'w').write(f'[map symbols {mp}]\n' + open(os.path.join(DOS, 'dsclog.asm')).read())
        subprocess.run(['nasm', '-f', 'bin', '-I', DOS + '/', '-o', out, src], check=True)
        found, section = {}, None
        for line in open(mp).read().splitlines():
            if line.startswith('---- Section '):
                section = line.split()[2]
            parts = line.split()
            if section in ('image', 'tail') and len(parts) == 3:
                try:
                    found[parts[2]] = (section, int(parts[1], 16))
                except ValueError:
                    pass
    return found


exe = open(os.path.join(DOS, 'DSCLOG.EXE'), 'rb').read()
image = exe[struct.unpack_from('<H', exe, 8)[0] * 16:]
tail_paras, = struct.unpack_from('<H', image, 1836)
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0xA0000, 0x100000, 16) if mem[i:i + 8] == b'DSCLOGva')
seg = hdr // 16
w = lambda a: struct.unpack_from('<H', mem, a)[0]
tail_seg = w(hdr + 1834)
print('header %05X (segment %04X); far_seg %04X; tail_seg %04X (%s: the image + %04X); EXE %d bytes'
      % (hdr, seg, w(hdr + 142), tail_seg, 'right' if tail_seg == seg + tail_paras else 'WRONG',
         tail_paras, len(exe)))
sym = symbols()
bad = 0
for name in sys.argv[1:] or CHECK:
    section, off = sym[name]
    base = hdr if section == 'image' else tail_seg * 16
    src = image[off:off + 40] if section == 'image' else image[tail_paras * 16 + off:tail_paras * 16 + off + 40]
    same = mem[base + off:base + off + 40] == src
    bad += not same
    print('  %-18s %s +%04X: %s' % (name, section, off, 'same' if same else 'DIFFERS'))
table = struct.unpack_from('<H', image, 144)[0]
vectors, at, vectors_ok = 0, table, True
while image[at]:
    vec, handler = image[at], struct.unpack_from('<H', image, at + 1)[0]
    ok = struct.unpack_from('<HH', mem, vec * 4) == (handler, seg)
    vectors += 1
    if not ok:
        bad += 1
        vectors_ok = False
        print('  vector %02Xh: %04X:%04X, not its handler %04X:%04X' % ((vec,) + struct.unpack_from('<HH', mem, vec * 4)[::-1] + (seg, handler)))
    at += 3
print('vectors in the table: %d, %s' % (vectors, 'all at their handlers' if vectors_ok else 'see above'))
for name, end in (('extra_types', 'extra_types_end'), ('extra_names', 'tail_end')):
    lo, hi = sym[name][1], sym[end][1]
    same = mem[tail_seg * 16 + lo:tail_seg * 16 + hi] == image[tail_paras * 16 + lo:tail_paras * 16 + hi]
    bad += not same
    print('  tail %-12s +%04X-%04X: %s' % (name, lo, hi, 'same as the EXE' if same else 'DIFFERS'))
print('OK' if not bad else 'NOT THE BUILD (%d)' % bad)
