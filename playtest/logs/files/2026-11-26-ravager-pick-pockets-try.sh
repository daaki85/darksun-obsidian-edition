# 2026-11-26-ravager-pick-pockets-try.sh TAG X Y: USE, the purse, a click on game X,Y, a grab, the dice log's tail, Continue
cd "$(dirname "$0")/../.."; export PLAYTEST_WORK=/tmp/playtest DISPLAY=:55
c(){ timeout 30 python3 ravclick.py "$@" >/dev/null; }
c 22 17; sleep 2; c 156 144; sleep 2; c $2 $3; sleep 3
W=$(xdotool search --pid $(cat /tmp/playtest/rav.pid) | tail -1); import -window $W /tmp/playtest/pp-$1.png
tail -5 /tmp/playtest/pp-dice.out; timeout 60 python3 logs/files/2026-11-26-ravager-pick-pockets-hdr.py | head -1
c 22 157; sleep 2
