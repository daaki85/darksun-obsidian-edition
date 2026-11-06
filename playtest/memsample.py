# memsample.py [LABEL]: one line of the game's memory: the map's flag, the heap, its free blocks, DOS memory free after the game.
import sys, struct
import os; PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT); __file__ = os.path.join(PT, 'live.py')
exec(open(__file__).read())
from dsloader import heapcheck
m = heapcheck.sample(g.read, gd.load_seg)
op = struct.unpack('<H', g.read(gd.ds*16 + heapcheck.MAP_OPEN, 2))[0]
print(sys.argv[1] if len(sys.argv) > 1 else '', 'map', op, 'heap', m.heap, 'heapfree', m.free, 'dosfree', m.dos_free, 'largest', m.dos_largest)
