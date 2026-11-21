# savediff.py A.SAV B.SAV [-v]: two saves (or any two GFF files) compared chunk by chunk
# (dsloader/gff.py's read_gff): the chunks only one has, and for each chunk both have that differs,
# its size in each and how many bytes differ (with -v, the first differing offsets and bytes).
# Then each file's name (STXT 1) and the journal's id (SAVE chunk 30, words 198 and 199).
import sys, os, struct
PT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(PT), 'obsidian-edition'))
from dsloader.gff import read_gff
names = [a for a in sys.argv[1:] if a != '-v']
verbose = '-v' in sys.argv
a, b = (read_gff(open(n, 'rb').read()) for n in names)
print('%s: %d bytes, %d chunks; %s: %d bytes, %d chunks' % (names[0], os.path.getsize(names[0]), len(a),
                                                               names[1], os.path.getsize(names[1]), len(b)))
for key in sorted(set(a) - set(b)):
    print('  only in the first:  %s %d (%d bytes)' % (key[0], key[1], len(a[key])))
for key in sorted(set(b) - set(a)):
    print('  only in the second: %s %d (%d bytes)' % (key[0], key[1], len(b[key])))
same = 0
for key in sorted(set(a) & set(b)):
    x, y = a[key], b[key]
    if x == y:
        same += 1
        continue
    where = [i for i in range(min(len(x), len(y))) if x[i] != y[i]]
    print('  differs: %s %d: %d and %d bytes, %d bytes differ' % (key[0], key[1], len(x), len(y), len(where)))
    if verbose:
        for i in where[:24]:
            print('      +%04X: %02X %02X' % (i, x[i], y[i]))
print('  %d chunks the same' % same)
for n, chunks in zip(names, (a, b)):
    text = chunks.get(('STXT', 1), b'').split(b'\0')[0].decode('cp437', 'replace')
    numbers = chunks.get(('SAVE', 30))
    head = struct.unpack_from('<HH', numbers, 198 * 2) if numbers and len(numbers) >= 400 else None
    print('  %s: name %r, journal id %s' % (os.path.basename(n), text, head[1] << 16 | head[0] if head else '?'))
