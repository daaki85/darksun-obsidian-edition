# state.py: one line of the game's state: fight (fight_on, whose turn), region, the leader's map
# position, the camera, and the flags named on the command line (state.py 11 505)
import sys, os, struct
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live.py')).read())
flags = ' '.join(f'flag{n}={int(gd.flag(int(n)))}' for n in sys.argv[1:])
print(f"fight_on {int(gd.fight_on())} turn {gd.whose_turn()} region {gd.region():#x} leader {gd.party_position()} "
      f"camera {struct.unpack('<hh', g.read(ds * 16 + CAMERA, 4))} {flags}")
