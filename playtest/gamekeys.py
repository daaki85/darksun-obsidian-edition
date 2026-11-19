# gamekeys.py [dis START [LEN]]: the keys the game itself acts on with the map up, read from DSUN.EXE
# ($DS_GAME): the root's table at 1BC5Bh (26 keys, then their handlers), the map overlay's at 71C1Bh
# (overlay 4272h: 33 keys) and that overlay's jump table for the letters c to v (71BE3h), each key
# with its handler's place in the file. A letter whose handler is the routine's end (71BA0h) does
# nothing. `dis START [LEN]` disassembles the file from START (hex; needs capstone), to read a handler.
# An overlay's routine is found from its stub in the root (segment S: file 5400h + S x 16): the
# dword at the stub's +4, plus 52EB0h, is the overlay's start; an entry's "CD 3F" is followed by
# the routine's offset in it (logs/2026-11-18-modernisation-features.md).
import os
import struct
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import GAME

f = open(os.path.join(GAME, 'DSUN.EXE'), 'rb').read()
if len(sys.argv) > 1 and sys.argv[1] == 'dis':
    import capstone
    start = int(sys.argv[2], 16)
    n = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x60
    for i in capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16).disasm(f[start:start + n], start):
        print('%05X  %-22s %s %s' % (i.address, f[i.address:i.address + i.size].hex(), i.mnemonic, i.op_str))
    sys.exit()
NAMES = {0x011B: 'Esc', 0x0F09: 'Tab', 0x2D00: 'Alt+X', 0x2E03: 'Ctrl+C', 0x4700: 'Home', 0x4800: 'Up', 0x4900: 'PgUp',
         0x4B00: 'Left', 0x4D00: 'Right', 0x4F00: 'End', 0x5000: 'Down', 0x5100: 'PgDn', 0x3920: 'Space'}
NAMES.update({(0x3B + i) << 8: 'F%d' % (i + 1) for i in range(10)})
NAMES.update({(0x68 + i) << 8: 'Alt+F%d' % (i + 1) for i in range(10)})


def table(at, count, base, title):
    print(title)
    keys = struct.unpack_from('<%dH' % count, f, at)
    hands = struct.unpack_from('<%dH' % count, f, at + 2 * count)
    for key, hand in zip(keys, hands):
        name = NAMES.get(key) or (chr(key & 0xFF) if 32 < (key & 0xFF) < 127 else '?')
        print('  %04X %-7s -> %05X' % (key, name, base + hand))


table(0x1BC5B, 26, 0x1AC70, "the root's table (1BC5Bh):")
OVERLAY = 0x6FDD0  # (overlay 4272h's start in the file)
table(OVERLAY + 0x1E4B, 33, OVERLAY, "the map overlay's table (71C1Bh):")
print("the map overlay's letters (71BE3h):")
for i, hand in enumerate(struct.unpack_from('<20H', f, OVERLAY + 0x1E13)):
    print('  %s -> %05X%s' % (chr(0x63 + i), OVERLAY + hand, '  (nothing)' if OVERLAY + hand == 0x71BA0 else ''))
