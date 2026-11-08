# passto.sh N (PASS_LIMIT tries, default 60): pass party turns until member N's: a click above the member's figure opens its END
# menu (the screen's top-left block changes), then E (END TURN); never E without the menu
cd "$(dirname "$0")"
W=$(xdotool search --class dosbox | head -1)
for i in $(seq 1 ${PASS_LIMIT:-60}); do
  st=$(timeout 20 python3 state.py | head -1)
  echo "$st" | grep -q "fight_on 1" || { echo "NO FIGHT"; exit 1; }
  t=$(echo "$st" | sed 's/.*turn \([-0-9]*\).*/\1/')
  [ "$t" = "$1" ] && { echo "TURN $1"; exit 0; }
  case "$t" in 0|1|2|3)
    P=$(timeout 20 python3 memberpos.py $t | tail -1); x=${P% *}; y=${P#* }
    opened=no
    for dy in 8 12 4 16 20; do
      sh shot.sh /tmp/playtest/pa.png >/dev/null 2>&1
      timeout 15 python3 click.py $x $((y-dy)) >/dev/null; sleep 1
      sh shot.sh /tmp/playtest/pb.png >/dev/null 2>&1
      if python3 - <<'PY'
from PIL import Image, ImageChops
a=Image.open('/tmp/playtest/pa.png').convert('RGB'); b=Image.open('/tmp/playtest/pb.png').convert('RGB')
d=ImageChops.difference(a,b)
# the END menu: a box about 190 x 55 somewhere on screen: count changed pixels
n=sum(1 for p in d.getdata() if max(p)>40)
raise SystemExit(0 if n>6000 else 1)
PY
      then opened=yes; break; fi
      st2=$(timeout 20 python3 state.py | head -1); echo "$st2" | grep -q "turn $t " || break
    done
    [ $opened = yes ] && { xdotool key --window $W e; sleep 3; } || sleep 3;;
  *) sleep 3;;
  esac
done
echo GAVE-UP
