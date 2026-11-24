#!/bin/sh
# ravhold.sh [FOLDER]: a real Hold Person in Wake of the Ravager's first fight (the Draxans' ambush in
# Tyr), for the held-target rule (DSCLOG2's HELD_HIT, HELD_DAMAGE): ravstart.sh FOLDER (default
# $WORK/rav; RAV_LOADER=1 for the Loader's copy), Ar'anda taught Hold Person in memory (bit 30 of her
# known-spells bitset, the 15 bytes at 3F3DCh in this start: a test edit, never saved), the talk, the
# party walked up the street, the others' turns ended until Ar'anda's, and her USE screen up at LEVEL
# 3 ($WORK/hold-use.png): Fireball, Haste, Hold Person (ravclick.py 214 60). Then by hand: aim at a
# Draxan (ravclick.py X Y none: red under it; ravfight.py state for places), xdotool mousedown 1 /
# mouseup 1 (its save in the dice log); a right-click on bare floor to drop the spell pointer, Q to
# end her turn (with the pointer up the turn waits for ever), and Computer Control for all four (C,
# then the lower small icon by each portrait: 47,53 98,53 47,113 98,113). Kills nothing: stop an
# earlier DOSBox first. About 3 minutes.
. "$(dirname "$0")/env.sh"
F=${1:-$WORK/rav}
sh "$PT/ravstart.sh" "$F" || exit 1
P=$(cat "$WORK/rav.pid"); W=$(xdotool search --pid "$P" | tail -1)
python3 - "$P" <<'PY' || exit 1
import sys, os, argparse
sys.path.insert(0, os.path.join(os.environ['PT'], '..', 'obsidian-edition'))
from dsloader.__main__ import connect
g = connect(argparse.Namespace(pid=int(sys.argv[1]), host_base=None))
a = 0x3F3DC; b = bytearray(g.read(a, 15))
if b[:4] != bytes.fromhex('09290229'): sys.exit('Ar\'anda\'s bitset not at 3F3DCh: ' + b.hex())
b[3] |= 0x40; g.write(a, bytes(b)); print("Hold Person taught:", g.read(a, 15).hex(' '))
import struct
from dsloader import game
lv = os.environ.get('SCARE_LEVEL')            # MEMBER=LEVEL: its first class's level (sheet +1Eh), a test edit
if lv:
    m, l = map(int, lv.split('='))
    ds = game.find_data_segment(g); off, seg = struct.unpack('<HH', g.read(ds*16 + 0x19C5, 4))
    s = seg*16 + off + m*(0x48 if os.environ.get('RAV_LOADER') else 0x42); old = g.read(s + 0x1E, 1)[0]; g.write(s + 0x1E, bytes((l,)))
    print('member %d: level %d made %d' % (m, old, l))
PY
for i in 1 2 3 4; do xdotool key --window "$W" 3; sleep 2; xdotool key --window "$W" Return; sleep 2; done
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 2   # (captures the mouse)
cd "$PT"
python3 ravclick.py 160 45 >/dev/null; sleep 8       # the party up the street: the Draxans' fight starts
python3 ravfight.py until 0                           # every other member's turn ended (Q, E) until Ar'anda's
xdotool key --window "$W" Escape; sleep 1.5           # (a stray E may have opened Effects)
python3 ravcreatures.py "$WORK/scare-c0.txt"
# USE (C; the first C after a fight's keys is often lost: pressed until the title's orange is there)
for t in 1 2 3; do
  xdotool key --window "$W" c; sleep 2.5
  R=$(import -window "$W" -crop 1x1+314+48 -depth 8 txt:- 2>/dev/null | tail -1 | grep -o '([0-9]*' | head -1 | tr -d '(')
  [ "${R:-0}" -gt 200 ] && break
done
python3 ravclick.py 197 171 >/dev/null; sleep 1.5; python3 ravclick.py 197 171 >/dev/null; sleep 1.5
import -window "$W" "$WORK/hold-use.png"






