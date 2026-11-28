# 2026-11-28-ravager-hdr.py (copied to /tmp/playtest/hdr.py): OFF [VALUE]: read (or write) a word of DSCLOG2's header in the running sequel
import os, sys, struct, argparse
sys.path.insert(0, '/home/claude/darksun-obsidian-edition/obsidian-edition')
from dsloader.__main__ import connect
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
mem = g.read(0, 0x110000); i = mem.find(b'DSCLOGR1')
off = int(sys.argv[1])
if len(sys.argv) > 2: g.write(i + off, struct.pack('<H', int(sys.argv[2])))
print(struct.unpack('<H', g.read(i + off, 2))[0])
