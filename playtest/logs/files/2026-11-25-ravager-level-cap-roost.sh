#!/bin/sh
# The level cap's rest: ravager-roost loaded on the Loader's copy (ravLC), the dice log attached, then
# (after the caller's edits) RESTGO=1 runs the Roost's route: Reyhan, a night, the corridor, the ring.
export PLAYTEST_WORK=/tmp/playtest/lcw DISPLAY=:58
cd /tmp/playtest/lckit/playtest
if [ -z "$RESTGO" ]; then
  timeout 200 sh ravload.sh ravager-roost /tmp/playtest/ravLC | tail -1
  RAV=/tmp/playtest/ravLC setsid nohup timeout 3000 python3 ravdice.py 2900 /tmp/playtest/lc-dice-rest.txt > /tmp/playtest/lc-dice-rest.out 2>&1 &
  echo $! > /tmp/playtest/lc-dice.pid; sleep 6; exit 0
fi
W=$(xdotool search --pid $(cat /tmp/playtest/lcw/rav.pid) | tail -1)
k() { for n in $(seq 1 $2); do xdotool key --window $W $1; sleep 0.4; done; }
python3 ravclick.py 160 100 right >/dev/null; sleep 1; python3 ravclick.py 160 100 right >/dev/null; sleep 1
python3 ravclick.py 150 128 >/dev/null; sleep 3
k 1 1; sleep 2; k 3 1; sleep 2; k 4 1; sleep 2; k space 1; sleep 2
import -window $W /tmp/playtest/lcw/r1.png
python3 ravclick.py 160 100 right >/dev/null; sleep 1
k Left 4; k Down 9; k Right 14; sleep 2
python3 ravclick.py 270 104 >/dev/null; sleep 4
k Up 6; sleep 2
python3 ravclick.py 160 100 right >/dev/null; sleep 1; python3 ravclick.py 160 100 right >/dev/null; sleep 1
import -window $W /tmp/playtest/lcw/r2.png
python3 ravclick.py 267 108 >/dev/null; sleep 12
import -window $W /tmp/playtest/lcw/r3.png
