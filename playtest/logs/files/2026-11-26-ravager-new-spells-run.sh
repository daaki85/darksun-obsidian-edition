#!/bin/sh
# 2026-11-26-ravager-new-spells-run.sh TAG [BITS] (from playtest/): ravSP (a fresh copy of rav) through the Loader's start
# (RAV_SKIP passes to ravstart.sh: a control), the dice log (ravdice.py --numbers, RAV_NO_SAVES=1), Ar'anda (member 0)
# taught the new spells in her sheet's bits (+3Fh |= BITS, default F8h: Cat's Grace 10h, Erdlu Claw 20h, Fogbolt 40h,
# Reflected Image 08h, Spook 80h; +3Dh |= 80h Friends: a test edit, never saved) and HP 250 for all four, the talk, the
# party up the street to the Draxans' fight (the class restrictions off, RAV_RULES_OFF default 0x2000: her armour), the others' turns ended until hers, her USE screen up ($WORK/sp-TAG-use.png).
PT=$(cd "$(dirname "$0")/../.." && pwd); cd $PT; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; TAG=$1; BITS=${2:-0xF8}; F=$W0/ravSP
rm -rf $F; cp -a $W0/rav $F
RAV_LOADER=1 RAV_STDOUT=1 timeout 200 sh ravstart.sh $F > $W0/sp-$TAG.start 2>&1 || { cat $W0/sp-$TAG.start; exit 1; }
P=$(cat $W0/rav.pid); W=$(xdotool search --pid "$P" | tail -1); echo $W > $W0/spw
: > $W0/sp-$TAG.txt
setsid nohup env RAV_NO_SAVES=1 RAV_RULES_OFF=${RAV_RULES_OFF-0x2000} timeout 3000 python3 ravdice.py --numbers 3000 $W0/sp-$TAG.txt > $W0/sp-$TAG.out 2>&1 &
echo $! > $W0/sp-$TAG.dpid
sleep 8
python3 - "$P" "$BITS" <<'PY' || exit 1
import sys, os, argparse, struct
sys.path.insert(0, os.path.join(os.getcwd(), '..', 'obsidian-edition'))
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(sys.argv[1]), host_base=None))
ds = game.find_data_segment(g); off, seg = struct.unpack('<HH', g.read(ds*16 + 0x19C5, 4))
s = seg*16 + off
b = bytearray(g.read(s, 0x48)); b[0x3F] |= int(sys.argv[2], 0); b[0x3D] |= 0x80; g.write(s, bytes(b))
print('Ar\'anda +3Dh %02X +3Fh %02X' % (g.read(s + 0x3D, 1)[0], g.read(s + 0x3F, 1)[0]))
PY
for m in 0 1 2 3; do timeout 30 python3 ravkits.py hp $m 250 >> $W0/sp-$TAG.kits 2>&1; done
for i in 1 2 3 4; do xdotool key --window "$W" 3; sleep 2; xdotool key --window "$W" Return; sleep 2; done
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 2
python3 ravclick.py 160 45 >/dev/null; sleep 8
timeout 200 python3 ravfight.py until 0
xdotool key --window "$W" Escape; sleep 1.5
for t in 1 2 3; do
  xdotool key --window "$W" c; sleep 2.5
  R=$(import -window "$W" -crop 1x1+314+48 -depth 8 txt:- 2>/dev/null | tail -1 | grep -o '([0-9]*' | head -1 | tr -d '(')
  [ "${R:-0}" -gt 200 ] && break
done
import -window "$W" $W0/sp-$TAG-use.png
echo "$TAG ready"
