#!/bin/sh
# pocket.sh MEMBER_X MEMBER_Y NAME [PURSE_X]: one pocket try: U, the thief's portrait on the USE screen (its
# position), the purse (157,145, a slow press; a cleric/thief has Turn Undead there and the purse at
# 177: PURSE_X), then the talk pointer on NAME (found from memory: its feet less 16), and the result
# window's Continue (the key 1). Prints the dice log's new lines.
cd "$(dirname "$0")"
. ./env.sh
W=$(xdotool search --class dosbox | head -1)
before=$(wc -l < "$WORK/dice.txt")
xdotool key --window $W u; sleep 1.5
timeout 10 python3 click.py $1 $2 >/dev/null; sleep 1.2
timeout 10 python3 click.py ${4:-157} 145 none >/dev/null; sleep 0.3; xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 1.5
P=$(timeout 10 python3 -c "
import os, struct, sys; HERE = os.getcwd(); __file__ = os.path.join(HERE, 'live.py'); exec(open(__file__).read())
cx, cy = struct.unpack('<HH', g.read(ds*16 + 0x1178, 4))
for t, c in gd.combatants().items():
    if gd.creature_name(c) == '$3':
        x, y = struct.unpack('<HH', g.read(ds*16 + 0x669D + t*32, 4)); print(x - cx, y - cy - 16)
")
timeout 10 python3 click.py $P >/dev/null; sleep 3
tail -n +$((before + 1)) "$WORK/dice.txt"
xdotool key --window $W 1; sleep 1.5  # (the result window: its Continue reply)
