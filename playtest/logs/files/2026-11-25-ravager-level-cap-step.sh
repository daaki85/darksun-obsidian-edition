#!/bin/sh
# lcstep.sh N: N times: grab, then act on what is up: CHOOSE A SPELL (beige scroll): its first spell;
# the powers' pop-up (dark): its first power; else the box (160,100). Prints what it did.
export PLAYTEST_WORK=/tmp/playtest/lcw DISPLAY=:58
cd /tmp/playtest/lckit/playtest
W=$(xdotool search --pid $(cat /tmp/playtest/lcw/rav.pid) | tail -1)
i=0
while [ $i -lt $1 ]; do
  i=$((i+1))
  import -window $W /tmp/playtest/lcw/step.png
  c=$(convert /tmp/playtest/lcw/step.png -format '%[pixel:p{330,300}] %[pixel:p{403,337}]' info:)
  case "$c" in
    srgb\(25[0-5],2[01][0-9],1[0-9][0-9]\)*) echo "$i spell $c"; cp /tmp/playtest/lcw/step.png /tmp/playtest/lcw/spell$i.png; timeout 20 python3 ravclick.py 120 73 >/dev/null;;
    *) case "$(convert /tmp/playtest/lcw/step.png -crop 300x30+180+265 +repage -format '%[fx:mean]' info:)" in
         0.[01]*) echo "$i psi $c"; cp /tmp/playtest/lcw/step.png /tmp/playtest/lcw/psi$i.png; timeout 20 python3 ravclick.py 122 61 >/dev/null;;
         *) echo "$i box $c"; timeout 20 python3 ravclick.py 160 100 >/dev/null;;
       esac;;
  esac
  sleep 3
done
