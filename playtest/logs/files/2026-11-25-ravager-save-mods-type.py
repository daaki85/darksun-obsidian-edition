# 2026-11-25-ravager-save-mods-type.py ITEM [TYPE]: an item record's type word (+0Ah), and a test edit of it (never
# saved): a member's weapon made the Cahulaks (type 24) for the THAC0 line's head names. Run from playtest/.
import sys, struct, argparse, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game, ravager
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
off, seg = struct.unpack('<HH', g.read(ds * 16 + ravager.ITEMS_PTR, 4))
at = seg * 16 + off + int(sys.argv[1]) * ravager.ITEM_SIZE + 0x0A
print('type', struct.unpack('<H', g.read(at, 2))[0])
if len(sys.argv) > 2:
    g.write(at, struct.pack('<H', int(sys.argv[2]))); print('now', struct.unpack('<H', g.read(at, 2))[0])
