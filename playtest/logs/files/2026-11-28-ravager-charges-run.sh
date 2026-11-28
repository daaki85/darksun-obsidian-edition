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
timeout 300 python3 ravfight.py until 3
xdotool key --window "$W" Tab; sleep 1.5; xdotool key --window "$W" Return; sleep 12
python3 /tmp/rs/play/charge.py 13; timeout 300 python3 ravfight.py until 3
xdotool key --window "$W" Tab; sleep 1.5; xdotool key --window "$W" Return; sleep 12
echo "after Gerakis's attack:"; python3 /tmp/rs/play/charge.py 13
timeout 300 python3 ravitems.py 3
timeout 300 python3 ravfight.py until 2
for t in 1 2 3; do xdotool key --window "$W" c; sleep 2.5; R=$(import -window "$W" -crop 1x1+314+48 -depth 8 txt:- 2>/dev/null | tail -1 | grep -o '([0-9]*' | head -1 | tr -d '('); [ "${R:-0}" -gt 200 ] && break; done
for i in 1 2 3 4 5; do python3 ravclick.py 197 171 >/dev/null; sleep 1.5; done
python3 ravclick.py 210 59 >/dev/null; sleep 2
import -window "$W" $O/heal-picked.png
python3 ravclick.py 116 58 >/dev/null; sleep 6
import -window "$W" $O/after-heal.png
echo done
