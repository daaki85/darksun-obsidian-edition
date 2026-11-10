# passn.sh N: pass N party turns (passuntil.sh's way: a click on the member's figure, the END menu checked
# by its grey pixels, E), the member's figure brought on screen with scroll.py first when the party
# stands spread out (2026-11-09: in fountain-user's ambush passuntil.sh stopped "member 2 off screen").
cd "$(dirname "$0")"; . ./env.sh
W=$(xdotool search --class dosbox | head -1)
for i in $(seq 1 $1); do
  t=$(timeout 10 python3 state.py | sed 's/.*turn \([-0-9]*\).*/\1/')
  case "$t" in 0|1|2|3)
    P=$(timeout 10 python3 memberpos.py $t | tail -1); x=${P% *}; y=${P#* }
    if [ $y -gt 150 ]; then timeout 30 python3 scroll.py 0 $((150 - y)) >/dev/null 2>&1; fi
    if [ $y -lt 40 ]; then timeout 30 python3 scroll.py 0 $((90 - y)) >/dev/null 2>&1; fi
    if [ $x -gt 280 ]; then timeout 30 python3 scroll.py $((200 - x)) 0 >/dev/null 2>&1; fi
    if [ $x -lt 20 ]; then timeout 30 python3 scroll.py $((120 - x)) 0 >/dev/null 2>&1; fi
    P=$(timeout 10 python3 memberpos.py $t | tail -1); x=${P% *}; y=${P#* }
    timeout 15 python3 click.py $x $y >/dev/null; sleep 1
    sh shot.sh $WORK/p1.png
    n=$(python3 -c "
from PIL import Image
im=Image.open('$WORK/p1.png').convert('RGB')
print(sum(1 for p in im.getdata() if 110<p[0]<200 and abs(p[0]-p[1])<12 and abs(p[1]-p[2])<25))" 2>/dev/null)
    if [ "$n" -gt 1300 ]; then xdotool key --window $W e; sleep 3; else echo "no menu for $t ($n) at $x $y"; sleep 2; fi;;
  *) sleep 3;;
  esac
done
