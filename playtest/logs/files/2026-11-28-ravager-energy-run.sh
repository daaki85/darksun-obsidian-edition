#!/bin/sh
# ec.sh TAG: Energy Control on Ar'anda by her own power, then Thy'rokh's Heal on her (RAV_SKIP from the caller)
sh /tmp/rs/play/start2.sh $1
cd /home/claude/darksun-obsidian-edition/playtest
export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
P=$(cat /tmp/playtest/rav.pid); W=$(xdotool search --pid "$P" | tail -1)
useup() { for t in 1 2 3; do xdotool key --window "$W" c; sleep 2.5; R=$(import -window "$W" -crop 1x1+314+48 -depth 8 txt:- 2>/dev/null | tail -1 | grep -o '([0-9]*' | head -1 | tr -d '('); [ "${R:-0}" -gt 200 ] && break; done; }
timeout 300 python3 ravfight.py until 0
useup; python3 ravclick.py 150 171 >/dev/null; sleep 1.5; python3 ravclick.py 195 171 >/dev/null; sleep 1.5
python3 ravclick.py 175 59 >/dev/null; sleep 6
timeout 300 python3 ravfight.py until 2
python3 -c "
import sys, struct, argparse
sys.path.insert(0, '/home/claude/darksun-obsidian-edition/obsidian-edition')
from dsloader.__main__ import connect
from dsloader import game
g = connect(argparse.Namespace(pid=int(open('/tmp/playtest/rav.pid').read()), host_base=None))
ds = game.find_data_segment(g)
o, s = struct.unpack('<HH', g.read(ds*16 + 0x19C9, 4))
g.write(s*16+o, struct.pack('<H', 20)); print('HP 20')"
useup; for i in 1 2 3 4 5; do python3 ravclick.py 197 171 >/dev/null; sleep 1.5; done
python3 ravclick.py 210 59 >/dev/null; sleep 2; import -window "$W" /tmp/rs/play/$1/heal-picked.png
python3 ravclick.py 70 58 >/dev/null; sleep 6; import -window "$W" /tmp/rs/play/$1/after.png
echo done
