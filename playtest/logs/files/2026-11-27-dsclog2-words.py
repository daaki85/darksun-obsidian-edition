import sys, struct, argparse
sys.path.insert(0,'/home/claude/darksun-obsidian-edition/obsidian-edition'); sys.path.insert(0,'/home/claude/darksun-obsidian-edition/obsidian-edition/tests')
from test_dsclog_drawing import build
from dsloader.__main__ import connect
exe, sym = build('/home/claude/darksun-obsidian-edition/obsidian-edition/dos/dsclog2.asm')
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
seg = int(sys.argv[1], 16)
for n in sys.argv[2:]:
    print(n, hex(sym[n]), struct.unpack('<H', g.read(seg*16 + sym[n], 2))[0])
