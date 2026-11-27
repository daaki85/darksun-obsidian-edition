# 2026-11-27-ravager-spell-arrows-hdr.py: read DSCLOG2's spell arrows header fields (+2098..+2113)
import sys, os, struct, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
pid = int(open('/tmp/playtest/rav.pid').read())
g = connect(argparse.Namespace(pid=pid, host_base=None))
mem = g.read(0, 0x100000)
i = mem.find(b"DSCLOGR1")
print('hdr', hex(i))
names = 'on seq reply who row shown late drawn'.split()
print(dict(zip(names, struct.unpack('<8H', mem[i+2098:i+2114]))))
