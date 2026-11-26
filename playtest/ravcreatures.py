# ravcreatures.py [OUT] [PID]: Wake of the Ravager's creature records (31h bytes each, at the far pointer
# DS:19C9h; +0 hit points, +6 the creature's id, 8019h-8016h the party), a line each: number, name, HP and
# the record in hex, to OUT (default: printed). Diff two runs round an action to see who it touched. The
# region's people are all listed, here or not (Tyr's start: 37).
import sys, os, struct, argparse, re
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(PT, '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
work = os.environ.get('PLAYTEST_WORK', '/tmp/playtest')
pid = int(sys.argv[2]) if len(sys.argv) > 2 else int(open(os.path.join(work, 'rav.pid')).read())
g = connect(argparse.Namespace(pid=pid, host_base=None)); ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds*16 + 0x19C9, 4)); b = g.read(seg*16 + off, 0x31*80)
lines = []
for i in range(80):
    r = b[i*0x31:(i+1)*0x31]; s = re.findall(rb"[A-Za-z' ]{3,}", r)
    if s and r[6:8] != b'\0\0' or i < 4:
        lines.append('%2d %-16s %4d  %s' % (i, s[0].decode() if s else '-', struct.unpack_from('<h', r, 0)[0], r.hex(' ')))
out = '\n'.join(lines) + '\n'
(open(sys.argv[1], 'w').write(out) if len(sys.argv) > 1 else print(out, end=''))
