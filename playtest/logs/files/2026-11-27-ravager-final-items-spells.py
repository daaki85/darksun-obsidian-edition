# spells.py FILE [SPELL EFFECT]: print the sequel's spell records (time +7, effect +19h, name) for the known
# spells; with SPELL EFFECT, write that effect byte in place (a test edit of the Loader's copy).
import sys, struct
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader import gff
path = sys.argv[1]
data = bytearray(open(path, 'rb').read())
places = gff.index_places(bytes(data), 'DATA')
def rec(s):
    _, off, ln = places[s]; return off, bytes(data[off:off+ln])
if len(sys.argv) > 3:
    s, e = int(sys.argv[2]), int(sys.argv[3]); off, r = rec(s)
    print('was', r[0x19])
    with open(path, 'r+b') as f: f.seek(off+0x19); f.write(bytes([e]))
    print('now', e)
else:
    for s in [0, 3, 8, 11, 13, 17, 24, 27, 29, 16, 20, 21]:
        off, r = rec(s)
        print(s, 'time', struct.unpack_from('<h', r, 7)[0], 'perlvl', struct.unpack_from('<H', r, 5)[0], 'effect', r[0x19], r[32:64].split(b'\0')[0])
