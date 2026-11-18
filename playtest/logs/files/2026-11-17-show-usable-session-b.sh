#!/bin/sh
# session B: fountain-user: marks in a second save, a fight begun while Alt is held, the Tab ring
# and the names in it, bodies after it
export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55
PT=$(cd "$(dirname "$0")/../.." && pwd)
O=$PLAYTEST_WORK/usable-out; mkdir -p $O
cd $PT
echo "--- the picture: pens-after-arena, the guard room, Alt held"
timeout 150 sh loadsave.sh pens-after-arena | tail -1
W=$(xdotool search --class dosbox | head -1)
timeout 60 python3 viewto.py 1380 440 | tail -1
for xy in "150 100" "120 80" "230 110"; do
  timeout 20 python3 click.py $xy none | tail -1
  xdotool keydown --window $W Alt_L; sleep 1.5
  timeout 20 python3 usable.py | grep named
  timeout 10 import -window $W "$O/pic-$(echo $xy | tr ' ' '-').png"
  xdotool keyup --window $W Alt_L; sleep 0.7
done
timeout 10 import -window $W $O/pic-off.png
timeout 150 sh loadsave.sh fountain-user | tail -1
W=$(xdotool search --class dosbox | head -1); xdotool getwindowgeometry $W | tail -1
sh guard_start.sh
tail -3 /tmp/playtest/dice.txt | cut -c1-160
(timeout 420 python3 altflag.py watch 400 > $O/fightwatch.txt 2>&1 &)
sleep 1
echo "--- Alt held (the key itself) before the fight"
xdotool keydown --window $W Alt_L; sleep 1.5
timeout 20 python3 usable.py
timeout 10 import -window $W $O/fountain-held.png
echo "--- the speech clicked away with Alt held: the fight starts"
timeout 90 sh dismiss.sh 8 | tail -4 | cut -c1-160
sleep 3; timeout 20 python3 state.py; timeout 20 python3 altflag.py
timeout 10 import -window $W $O/fountain-fight-held.png
echo "--- Tab with Alt still held, then without"
xdotool key --window $W Tab; sleep 1.5; timeout 20 python3 altflag.py; timeout 10 import -window $W $O/fountain-alt-tab.png
xdotool keyup --window $W Alt_L; sleep 0.5
xdotool key --window $W Tab; sleep 1.5; timeout 20 python3 altflag.py; timeout 10 import -window $W $O/fountain-tab.png
echo "--- the fight fought out, Alt held during the foes' turns"
(timeout 320 python3 $PT/logs/files/2026-11-17-show-usable-flagfoes.py $PT 300 > $O/flagfoes.txt 2>&1 &)
timeout 300 sh fightout.sh 40 | tail -3 | cut -c1-160
timeout 20 python3 state.py; timeout 20 python3 altflag.py
grep -c -- '-> miss' /tmp/playtest/dice.txt
for p in $(pgrep -f "flagfoe[s].py"); do kill $p; done; sleep 0.5; xdotool keyup --window $W Alt_L
echo "--- after the fight: bodies"
timeout 60 sh dismiss.sh 6 | tail -2 | cut -c1-160
sleep 2; xdotool keydown --window $W Alt_L; sleep 1.5
timeout 20 python3 usable.py; timeout 20 python3 altflag.py
timeout 20 python3 bodyitems.py | grep 'body thing'
timeout 10 import -window $W $O/fountain-bodies.png
echo "--- a click with Alt held: a slow press on the first body in view"
timeout 20 python3 pointer.py walk | tail -1
XY=$(timeout 20 python3 bodyitems.py | awk '/body thing/ && $5 > 20 && $5 < 300 && $6 > 40 && $6 < 190 {print $5, $6 - 4; exit}')
echo "body at $XY"
timeout 20 python3 click.py $XY none | tail -1; sleep 0.4
xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 2.5
timeout 10 import -window $W $O/fountain-body-click.png
tail -3 /tmp/playtest/dice.txt | cut -c1-160
xdotool keyup --window $W Alt_L
kill $(cat /tmp/playtest/guard.pid)
for p in $(pgrep -f "^python3 -u -m dsloade[r]"); do kill $p; done
for p in $(pgrep -x dosbox); do kill $p; done
echo SESSION B DONE
