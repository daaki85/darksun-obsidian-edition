#!/bin/sh
# session D: after the rebase onto the quick save and chance-to-hit work (the helper rebuilt):
# the build in place, the marks up and down in pens-after-arena. No memory edit, no fight.
export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55 PT_KEEP_OTHERS=1
PT=$(cd "$(dirname "$0")/../.." && pwd)
O=$PLAYTEST_WORK/usable-out; mkdir -p $O
cd $PT
timeout 150 sh loadsave.sh pens-after-arena | tail -1
W=$(xdotool search --class dosbox | head -1); xdotool getwindowgeometry $W | tail -1
MYBOX=$(pgrep -n -x dosbox); MYLOG=$(pgrep -n -f "^python3 -u -m dsloade[r] dicelog$"); echo "this session's DOSBox $MYBOX, dice log $MYLOG"
timeout 90 python3 buildcheck.py | tail -1
sh guard_start.sh
timeout 60 python3 viewto.py 1380 440 | tail -1
timeout 20 python3 click.py 150 100 none | tail -1
xdotool keydown --window $W Alt_L; sleep 1.5
timeout 20 python3 usable.py | head -16
timeout 20 python3 altflag.py
timeout 10 import -window $W $O/rebased-held.png
xdotool keyup --window $W Alt_L; sleep 1
timeout 20 python3 altflag.py
timeout 30 python3 altflag.py latency 3
echo "--- a door opened with Alt held (the look pointer), from beside it"
timeout 20 python3 pointer.py walk | tail -1
timeout 60 python3 route.py 1576 472 | tail -1
timeout 60 python3 viewto.py 1560 460 | tail -1
timeout 30 python3 doors.py | grep '(95, 2'
timeout 20 python3 state.py
timeout 30 python3 pointer.py look | tail -1
xdotool keydown --window $W Alt_L; sleep 1
XY=$(timeout 20 python3 usable.py | awk '/thing 255 / {split($8, a, ","); print a[1], a[2] - 18}')
echo "door leaf at $XY"; timeout 20 python3 click.py $XY none | tail -1; sleep 0.4
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 3
timeout 10 import -window $W $O/rebased-door.png
xdotool keyup --window $W Alt_L; sleep 0.5
tail -2 $PLAYTEST_WORK/dice.txt | cut -c1-160
timeout 30 python3 doors.py | grep '(95, 2' || echo "door square (95, 28) no longer shut"
timeout 30 python3 pointer.py walk | tail -1
tail -3 $PLAYTEST_WORK/dice.txt | cut -c1-160
kill $(cat $PLAYTEST_WORK/guard.pid)
kill $MYLOG; kill $MYBOX
echo SESSION D DONE
