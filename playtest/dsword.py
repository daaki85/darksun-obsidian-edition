# dsword.py ADDR [VALUE]: the game's DS word at ADDR (hex), or set it (memory only). E.g. dsword.py 5E6:
# the thing whose container window is open (9999 none: 2026-11-11, looting).
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
at = int(sys.argv[1], 16)
if len(sys.argv) > 2:
    g.write(ds * 16 + at, struct.pack('<H', int(sys.argv[2], 0)))
print(hex(at), struct.unpack('<H', g.read(ds * 16 + at, 2))[0])
