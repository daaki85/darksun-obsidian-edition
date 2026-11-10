# passuntil.sh N [MAX]: pass party turns until member N's: a click ON the figure (memberpos.py), the END
# menu checked by its grey pixels in a shot (over 1300; about 570 without), then E. A Stuck or Paralyzed
# member's turn opens with the menu already up, and the click there does no harm. MAX tries (40).
cd "$(dirname "$0")"; . ./env.sh
W=$(xdotool search --class dosbox | head -1)
for i in $(seq 1 ${2:-40}); do
  t=$(timeout 10 python3 state.py | sed 's/.*turn \([-0-9]*\).*/\1/')
  [ "$t" = "$1" ] && { echo "TURN $1"; exit 0; }
  case "$t" in 0|1|2|3)
    P=$(timeout 10 python3 memberpos.py $t | tail -1); x=${P% *}; y=${P#* }
    if [ $x -lt 5 -o $x -gt 315 -o $y -lt 25 -o $y -gt 195 ]; then echo "member $t off screen $P"; exit 2; fi
    timeout 15 python3 click.py $x $y >/dev/null; sleep 1
    sh shot.sh $WORK/p1.png
    n=$(python3 -c "
from PIL import Image
im=Image.open('$WORK/p1.png').convert('RGB')
print(sum(1 for p in im.getdata() if 110<p[0]<200 and abs(p[0]-p[1])<12 and abs(p[1]-p[2])<25))" 2>/dev/null)
    if [ "$n" -gt 1300 ]; then xdotool key --window $W e; sleep 3; else echo "no menu for $t ($n)"; sleep 3; fi;;
  *) sleep 3;;
  esac
done
echo GAVE-UP
