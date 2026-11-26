#!/bin/sh
# The high-level kits play (2026-11-26): the Loader's copy from ravLC to the Draxans' ambush, the dice log attached.
# RAV_SKIP may name the patches left out (the control: lv_weapons).
export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55
PT=$(cd "$(dirname "$0")/../.." && pwd)
cd $PT
RAV_LOADER=1 timeout 240 sh ravstart.sh /tmp/playtest/ravLC || exit 1
P=$(cat /tmp/playtest/rav.pid); W=$(xdotool search --pid "$P" | tail -1)
echo "dosbox $P window $W"
RAV=/tmp/playtest/ravLC setsid nohup timeout 3000 python3 ravdice.py 2900 /tmp/playtest/hl-dice${HL_TAG}.txt > /tmp/playtest/hl-dice${HL_TAG}.out 2>&1 &
echo $! > /tmp/playtest/hl-dice.pid
sleep 6
for i in 1 2 3 4; do xdotool key --window "$W" 3; sleep 2; xdotool key --window "$W" Return; sleep 2; done
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 2
python3 ravclick.py 160 45 >/dev/null; sleep 8
import -window "$W" /tmp/playtest/hl-fight${HL_TAG}.png
echo started
