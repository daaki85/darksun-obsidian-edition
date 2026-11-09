# slotcount.py [LABEL]: one line: the leader's place, the game's picture slots taken (of 300), the
# store's end (of 741,376), how many are in memory and STALE, and with DSCLOG's PIC_REUSE how many
# slots it has reused (pf_count, from a symbol map of the helper as built), for watching how a region
# fills the table (2026-11-09, logs/2026-11-09-picture-slots-explore.md, -picture-slot-reuse.md).
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
n = struct.unpack('<H', g.read(ds * 16 + 0x1F84, 2))[0]
tab = g.read((gd.load_seg + 0x3E60) * 16, n * 16)
ents = [struct.unpack_from('<HIiIBB', tab, k * 16) for k in range(n)]
end = max((e[2] + e[1] for e in ents if e[2] >= 0 and e[0] != 0xFFFE), default=0)
inmem = sum(1 for e in ents if e[4] & 2)
stale = sum(1 for e in ents if e[0] == 0xFFFE)
x, y = struct.unpack('<hh', g.read(ds * 16 + 0x669D, 4))
reused = '?'
try:
    import subprocess, tempfile
    dos = os.path.join(os.path.dirname(PT), 'obsidian-edition', 'dos')
    with tempfile.TemporaryDirectory() as tmp:
        src, out, mp = (os.path.join(tmp, f) for f in ('m.asm', 'm.bin', 'm.map'))
        open(src, 'w').write(f'[map symbols {mp}]\n' + open(os.path.join(dos, 'dsclog.asm')).read())
        subprocess.run(['nasm', '-f', 'bin', '-I', dos + '/', '-o', out, src], check=True)
        sym = next(int(l.split()[1], 16) for l in open(mp).read().split('Section image')[1].splitlines()
                   if len(l.split()) == 3 and l.split()[2] == 'pf_count')
    hdr = next(a for a in range(0xC0000, 0xF0000, 16) if g.read(a, 8) == b'DSCLOGva')
    reused = struct.unpack('<H', g.read(hdr + sym, 2))[0]
except Exception as e:
    reused = f'? ({e})'
print(f'{sys.argv[1] if len(sys.argv) > 1 else ""}: leader {x},{y} slots {n} store end {end} '
      f'({end * 100 // 741376}%) in memory {inmem} stale {stale} reused {reused}')
