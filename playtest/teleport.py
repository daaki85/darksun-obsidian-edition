# teleport.py X Y CX CY: the party (map objects 0-3) put at map X, Y and the camera at CX, CY, in
# memory (DS:669Dh + 32n, DS:1178h); then walk a step with walkto.py so the game redraws and makes the
# objects near. Only for checks where the way is shut: the scripts see none of it; never save after.
import os, sys, struct; HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'live.py')).read())
x, y, cx, cy = map(int, sys.argv[1:5])
for n in range(4):
    g.write(ds * 16 + 0x669D + 32 * n, struct.pack('<HH', x, y))
g.write(ds * 16 + CAMERA, struct.pack('<hh', cx, cy))
print('party at', (x, y), 'camera', (cx, cy))
