#!/bin/sh
# openshop.sh: from the "selling junk" save (saves/selling-junk-user), Kalzith's shop: the eye on him
# (his figure's square found from memory: his feet less 16), Talk, 1, the box clicked through, 1, the box.
cd "$(dirname "$0")"
. ./env.sh
W=$(xdotool search --class dosbox | head -1)
P=$(timeout 10 python3 -c "
import os, struct; HERE = os.getcwd(); __file__ = os.path.join(HERE, 'live.py'); exec(open(__file__).read())
cx, cy = struct.unpack('<HH', g.read(ds*16 + 0x1178, 4))
for t, c in gd.combatants().items():
    if gd.creature_name(c) == 'Kalzith':
        x, y = struct.unpack('<HH', g.read(ds*16 + 0x669D + t*32, 4)); print(x - cx, y - cy - 16)
")
timeout 30 python3 pointer.py look >/dev/null
timeout 10 python3 click.py $P none >/dev/null; sleep 0.5; xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 2
timeout 10 python3 click.py 163 86 none >/dev/null; sleep 0.3; xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 3
xdotool key --window $W 1; sleep 3
for i in 1 2 3 4; do sh boxclick.sh >/dev/null 2>&1; sleep 2; done
xdotool key --window $W 1; sleep 3; sh boxclick.sh >/dev/null 2>&1; sleep 3
sh shot.sh "$WORK/shop.png" >/dev/null 2>&1
