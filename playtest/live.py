# live.py: exec'd by the Python tools: g (the game's memory), ds (its data segment), gd (GameData,
# dsloader/game.py: party_position, region, flag, whose_turn, fight_on, creature...)
import sys, os, argparse, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import PT, REPO, WORK, GAME
sys.path.insert(0, os.path.join(REPO, 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
from dsloader.process import find_dosbox_processes
def _pid():
    # the test's own program when start_recomp.sh recorded it (other dsun processes may be
    # headless runs of the recompiled program); else the newest DOSBox or dsun
    f = os.path.join(WORK, 'dsun.pid')
    if os.path.exists(f):
        pid = int(open(f).read().split()[0])
        if os.path.exists(f'/proc/{pid}'):
            return pid
    return max(p for p, _ in find_dosbox_processes())
g = connect(argparse.Namespace(pid=_pid(), host_base=None))
ds = game.find_data_segment(g)
gd = game.GameData(g, ds)
CAMERA = 0x1178  # DS: the map view's top-left, x and y words: screen = map - camera, 1 unit a pixel
POINTER = 0xA133  # DS: the pointer, x and y in game pixels (320x200)
MAP_PTR = 0x556  # DS: far pointer to the live walkability grid of the region (128 x 98 bytes, one a
# 16-unit square, as RGNxx.GFF's GMAP but as now: closed doors and gates 192/193 and up, figures 96)
def live_map():
    off, seg = struct.unpack('<HH', g.read(ds * 16 + MAP_PTR, 4))
    return g.read(seg * 16 + off, 128 * 98)
