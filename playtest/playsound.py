# playsound.py N: have DSCLOG play sound N from the map's main loop (its header's SOUND_REQ, +1822): a game
# sound (0-130) or one of the mod's (140, 141). Prints "played" once DSCLOG took it.
import os, sys, struct, time; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
mem = g.read(0, 0x110000)
hdr = next(i for i in range(0, len(mem), 16) if mem[i:i + 8] == b'DSCLOGva')
n = int(sys.argv[1])
print('header at %X, sound_req %04X' % (hdr, struct.unpack('<H', g.read(hdr + 1822, 2))[0]))
g.write(hdr + 1822, struct.pack('<H', n))
for _ in range(40):
    time.sleep(0.1)
    if struct.unpack('<H', g.read(hdr + 1822, 2))[0] == 0xFFFF:
        print('played', n); break
else: print('not taken')
