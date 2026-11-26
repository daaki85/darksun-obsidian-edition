#!/bin/sh
# 2026-11-26-ravager-new-spells-levelup.sh TAG (from playtest/, after -run.sh TAG BITS KIT with the USE screen up):
# Ar'anda made a 5th-level preserver (ravlevel.py set: her best levels the same, so 6th is a new level), the
# Draxans' HP 1, the USE screen shut, Computer Control for all four, the fight's XP boxes clicked until
# CHOOSE A SPELL (beige) is up ($WORK/sp-TAG-pick.png). All test edits, never saved.
export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest; W0=/tmp/playtest; TAG=$1
W=$(xdotool search --pid $(cat $W0/rav.pid) | tail -1)
timeout 30 python3 ravlevel.py set 0 40000 3 11,12,17 5,6,7
timeout 30 python3 ravlevel.py foes 1 >/dev/null
xdotool key --window $W Escape; sleep 1.5; xdotool key --window $W c; sleep 2
for xy in "47 53" "98 53" "47 112" "98 112"; do timeout 20 python3 ravclick.py $xy >/dev/null; sleep 1; done; xdotool key --window $W Escape
for i in $(seq 1 30); do sleep 8; grep -q "receives" $W0/sp-$TAG.txt 2>/dev/null && break; done; sleep 3
for i in 1 2 3 4 5 6 7 8; do
  import -window $W $W0/sp-$TAG-pk.png; cp $W0/sp-$TAG-pk.png $W0/sp-$TAG-pk$i.png
  case "$(convert $W0/sp-$TAG-pk.png -format '%[pixel:p{220,200}]' info:)" in srgb\(25[0-5],2[01][0-9],1[0-9][0-9]\)) echo "pick up"; break;; esac
  timeout 20 python3 ravclick.py 300 185 >/dev/null; sleep 3
done
cp $W0/sp-$TAG-pk.png $W0/sp-$TAG-pick.png
