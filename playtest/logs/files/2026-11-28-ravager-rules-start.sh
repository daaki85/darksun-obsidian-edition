#!/bin/sh
# run.sh TAG: one run of the charges + Energy Control check (RAV_SKIP from the caller for the control)
cd /home/claude/darksun-obsidian-edition/playtest
export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest RAV_LOADER=1
T=$1; O=/tmp/rs/play/$T; mkdir -p $O
timeout 400 sh ravstart.sh > $O/start.txt 2>&1 || { echo start failed; exit 1; }
P=$(cat /tmp/playtest/rav.pid); W=$(xdotool search --pid "$P" | tail -1)
setsid nohup timeout 2000 python3 ravdice.py 1900 $O/dice.txt > $O/dice.out 2>&1 &
sleep 3
for i in 1 2 3 4; do xdotool key --window "$W" 3; sleep 2; xdotool key --window "$W" Return; sleep 2; done
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 2
python3 ravclick.py 160 45 >/dev/null; sleep 8
python3 /tmp/rs/play/setup.py
python3 /tmp/rs/play/setup.py; cd /home/claude/darksun-obsidian-edition/playtest; python3 ravkits.py power 0 7; echo ready
