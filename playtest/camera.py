# camera.py [X Y]: read the camera (the view's top-left, DS:1178h), or set it to X, Y (map units) to
# look somewhere the view won't scroll to by itself (it does not follow the leader everywhere)
import sys, os, struct
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
if len(sys.argv) > 2:
    g.write(ds * 16 + CAMERA, struct.pack('<hh', int(sys.argv[1]), int(sys.argv[2])))
print('camera', struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4)))
