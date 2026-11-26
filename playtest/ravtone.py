# ravtone.py [warm|neutral|show] [FLAG]: Wake of the Ravager wall shadows' tone (DSCLOG2's WS_GAIN, header + 5F8Bh) swapped in guest memory, DARK made again; FLAG the header's +1872 (shadows on 1, off 0). A test edit: never save after. Offsets for the 2026-11-22 build (check with nasm -l: WS_GAIN, WS_DAC_SUM).
import os, sys, struct, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'obsidian-edition'))
from dsloader.__main__ import connect
g=connect(argparse.Namespace(pid=int(open(os.path.join(os.environ.get('PLAYTEST_WORK','/tmp/playtest'),'rav.pid')).read()), host_base=None))
mem=g.read(0, 0x110000); i=mem.find(b'DSCLOGR1')
GAIN, SUM = i+0x5F8B, i+0x5FD1
T={'warm':(187,180,188,1393,-469,-72),'neutral':(189,189,189,0,0,0)}
cur=struct.unpack('<6h', g.read(GAIN,12)); print('now', cur)
assert cur in T.values(), 'not the tone table'
if len(sys.argv)>1 and sys.argv[1] in T:
    g.write(GAIN, struct.pack('<6h', *T[sys.argv[1]])); g.write(SUM, b'\0\0\0\0'); print('set', sys.argv[1])
if len(sys.argv)>2: g.write(i+1872, struct.pack('<H', int(sys.argv[2])))
print('flag', struct.unpack('<H',g.read(i+1872,2))[0], 'builds', struct.unpack('<H',g.read(i+1876,2))[0])
