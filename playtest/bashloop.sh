# bashloop.sh N: use Pehtucl's chest from beside it and answer Y to "Bash it open?" until the lock breaks (N tries)
cd "$(dirname "$0")"
W=$(xdotool search --class dosbox | head -1); D=/tmp/playtest/dice.txt
exitmenu() { sh shot.sh /tmp/playtest/bl.png >/dev/null 2>&1; python3 -c "
from PIL import Image
im=Image.open('/tmp/playtest/bl.png').convert('RGB'); px=[im.getpixel((x,y)) for x in range(100,220,4) for y in range(80,120,4)]
r=sum(c[0] for c in px)/len(px); b=sum(c[2] for c in px)/len(px); raise SystemExit(0 if b > r + 10 else 1)"; }
for i in $(seq 1 $1); do
  timeout 60 python3 pointer.py look >/dev/null
  timeout 10 python3 click.py 204 90 none >/dev/null; sleep 0.3; xdotool mousedown 1; sleep 0.15; xdotool mouseup 1; sleep 1.5
  timeout 10 python3 click.py 141 125 none >/dev/null; sleep 0.3; xdotool mousedown 1; sleep 0.15; xdotool mouseup 1
  for t in 1 2 3 4 5 6; do sleep 1; tail -1 $D | grep -q "2. No" && break; done
  tail -1 $D | grep -q "2. No" || { echo "try $i: no question"; tail -2 $D; exit 1; }
  xdotool key --window $W y; sleep 3
  if tail -6 $D | grep -q "breaking it open"; then echo "BROKE on try $i"; exit 0; fi
  for k in 1 2 3; do sh msgbox.sh >/dev/null 2>&1 && { sh boxclick.sh >/dev/null 2>&1; sleep 1.2; }; done
  sleep 1; xdotool key --window $W Escape; sleep 1.2
  exitmenu && { timeout 10 python3 click.py 120 116 >/dev/null; sleep 1; }
done
echo "no break in $1"
