#!/bin/sh
# session C: fountain-user after its fight: a click on a body with Alt held, then the same without
export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55
PT=$(cd "$(dirname "$0")/../.." && pwd)
O=$PLAYTEST_WORK/usable-out; mkdir -p $O
cd $PT
timeout 150 sh loadsave.sh fountain-user | tail -1
W=$(xdotool search --class dosbox | head -1)
sh guard_start.sh
timeout 90 sh dismiss.sh 8 | tail -1 | cut -c1-120
timeout 300 sh fightout.sh 40 | tail -1 | cut -c1-160
timeout 60 sh dismiss.sh 6 | tail -1 | cut -c1-120
timeout 20 python3 pointer.py walk | tail -1
press() {  # a slow press on the first body in view, then a grab 6 s later
  XY=$(timeout 20 python3 bodyitems.py | awk '/body thing/ && $5 > 20 && $5 < 300 && $6 > 40 && $6 < 190 {print $5, $6 - 4; exit}')
  timeout 20 python3 state.py
  echo "$1: body at $XY"; timeout 20 python3 click.py $XY none | tail -1; sleep 0.4
  xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 6
  timeout 10 import -window $W $O/body-$1.png; timeout 20 python3 state.py
}
xdotool keydown --window $W Alt_L; sleep 1
press alt
xdotool keyup --window $W Alt_L; sleep 1
timeout 10 import -window $W $O/body-alt-released.png
press plain
kill $(cat /tmp/playtest/guard.pid)
for p in $(pgrep -f "^python3 -u -m dsloade[r]"); do kill $p; done
for p in $(pgrep -x dosbox); do kill $p; done
echo SESSION C DONE
