# 2026-11-28-ravager-shadows-onoff.sh TAG: two grabs of the sequel's view, the walls' and figures' shadows off (DSCLOG2 header +1872, +1960 = 0), then on; U then Escape draws the view again. Uses 2026-11-28-ravager-hdr.py as /tmp/playtest/hdr.py.
# onoff.sh TAG: grabs of the view with the walls' and figures' shadows off, then on (U, Escape to redraw)
W=$(xdotool search --pid $(cat /tmp/playtest/rav.pid) | tail -1)
for v in 0 1; do python3 /tmp/playtest/hdr.py 1872 $v >/dev/null; python3 /tmp/playtest/hdr.py 1960 $v >/dev/null
xdotool key --window $W u; sleep 1.5; xdotool key --window $W Escape; sleep 1.5; import -window $W /tmp/playtest/$1_$v.png; done
