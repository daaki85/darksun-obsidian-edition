# setpic.py THING PICTURE: a map thing drawn with another walking picture (memory only, never save)
import os, sys, struct
PT = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, PT)
exec(open(os.path.join(PT, 'live.py')).read())
t, pic = int(sys.argv[1]), int(sys.argv[2])
at = ds * 16 + 0x6694 + t * 32
old, = struct.unpack('<H', g.read(at + 0x18, 2))
g.write(at + 0x18, struct.pack('<H', pic)); g.write(at + 0x0F, struct.pack('<H', 0xFFFF))
flags = g.read(at, 1)[0]; g.write(at, bytes([flags | 1]))
print('thing', t, 'picture', old, '->', pic)
