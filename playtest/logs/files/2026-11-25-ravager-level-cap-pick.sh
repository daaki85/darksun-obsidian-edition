#!/bin/sh
# The preserver's CHOOSE A SPELL at a 21st-level level up: Ar'Anda preserver 21 at 4,861,000 XP (the fight's
# 14,000 makes 23rd: two windows), the ambush won, the first window grabbed, then LEVEL pressed 11 times;
# THAC=1 also a fighter 26, psionicist 23 and human cleric 26 (THAC0 past 20th), STEPS=N lcstep.sh after.
export PLAYTEST_WORK=/tmp/playtest/lcw DISPLAY=:58
cd /tmp/playtest/lckit/playtest
timeout 330 sh lcgo.sh | tail -1
python3 ravlevel.py set 0 4861000 3 11 21
if [ -n "$THAC" ]; then   # (the THAC0 replay: a fighter 26, a psionicist 23, a human cleric 26)
  python3 ravlevel.py set 3 5600000 5 9 26; python3 ravlevel.py set 2 5600000 8 12 23; python3 ravlevel.py set 1 4700000 1 2 26
fi
W=$(xdotool search --pid $(cat /tmp/playtest/lcw/rav.pid) | tail -1)
python3 ravlevel.py foes 1 >/dev/null; xdotool key --window $W c; sleep 2
for xy in "47 53" "98 53" "47 112" "98 112"; do python3 ravclick.py $xy >/dev/null; sleep 1; done; xdotool key --window $W Escape
for i in $(seq 1 25); do sleep 8; grep -q "receives" /tmp/playtest/lc-dice$LC_TAG.txt 2>/dev/null && break; done; sleep 3
for i in 1 2 3 4 5 6; do
  import -window $W /tmp/playtest/lcw/pk.png
  case "$(convert /tmp/playtest/lcw/pk.png -format '%[pixel:p{330,300}]' info:)" in srgb\(25[0-5],2[01][0-9],1[0-9][0-9]\)) break;; esac
  python3 ravclick.py 300 185 >/dev/null; sleep 3
done
cp /tmp/playtest/lcw/pk.png /tmp/playtest/lcw/pick$LC_TAG-open.png
for n in $(seq 1 11); do python3 ravclick.py 110 147 >/dev/null; sleep 1.5; import -window $W /tmp/playtest/lcw/pick$LC_TAG-$n.png; done
sh lcstep.sh ${STEPS:-0} | tail -1; python3 ravlevel.py show | sed 's/casts left.*//'
cd /tmp/playtest/lcw; convert pick$LC_TAG-open.png $(for n in $(seq 1 11); do echo pick$LC_TAG-$n.png; done) -crop 120x30+170+338 +repage -append pick$LC_TAG-pages.png
