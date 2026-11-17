#!/bin/sh
# picpattern.sh WHERE:SCALE:PICTURE ...: the Loader's display settings (launch.display_lines) tried
# in a DOSBox of its own, without the game and without the DOSBox lock: a 33-byte program puts a
# pattern on the game's screen mode (13h, 320x200) and waits. WHERE is win or full, SCALE 1-4,
# PICTURE plain, scanlines, tv or sharp: "win:4:scanlines full:3:sharp". For each it prints the
# settings, the window's size and DOSBox's complaints, and grabs the window (the whole screen for
# full) to $WORK/picpattern/WHERE-SCALE-PICTURE.png.
# It can't disturb a play: its own display (:57, 1920x1080, so the 1280x960 window and full screen
# fit), its own folder as C:, and DOSBox run under another name (a copy called dbpat), so the
# kit's tools (live.py takes the newest process named dosbox; start.sh's pkill -x dosbox) and
# other agents' never see it. Its window's class is then dbpat too.
. "$(dirname "$0")/env.sh"
D=$WORK/picpattern; mkdir -p "$D/c"; export DISPLAY=:57
[ -x "$D/dbpat" ] || cp "$(command -v dosbox)" "$D/dbpat"
python3 -c "
open('$D/c/PAT.COM', 'wb').write(bytes.fromhex(
    'B81300CD10' 'B800A08EC0' '31FF' '89F830E0AA' '81FF00FA75F5' '31C0CD16' 'B80300CD10' 'C3'))"
# (mode 13h; ES = A000; each byte its offset's low byte xor its high byte; a key; text mode; out)
pgrep -f "Xvfb :5[7]" >/dev/null || (Xvfb :57 -screen 0 1920x1080x24 >/dev/null 2>&1 &); sleep 2
for spec in "$@"; do
  full=${spec%%:*}; rest=${spec#*:}; scale=${rest%%:*}; pic=${rest#*:}; name=$full-$scale-$pic
  (cd "$REPO/obsidian-edition" && python3 -c "
from dsloader import launch
lines = launch.display_lines({'fullscreen': '$full' == 'full', 'window_scale': $scale, 'picture': '$pic'})
lines += ['[autoexec]', 'mount c \"$D/c\"', 'c:', 'pat.com', 'exit', '']
open('$D/$name.conf', 'w').write('\n'.join(lines))")
  (cd "$D" && SDL_AUDIODRIVER=dummy setsid ./dbpat -conf "$GAME/__support/app/dosbox_darksun.conf" -conf "$D/$name.conf" > "$D/$name.log" 2>&1 < /dev/null &)
  sleep 4
  W=$(timeout 5 xdotool search --class dbpat | head -1)
  echo "== $name: $(sed '/autoexec/,$d' "$D/$name.conf" | tr '\n' ' ')"
  timeout 5 xdotool getwindowgeometry $W | grep Geometry
  if [ "$full" = full ]; then timeout 10 import -window root "$D/$name.png"; else timeout 10 import -window $W "$D/$name.png"; fi
  grep -i 'opengl\|SDL:\|scaler\|exit to error' "$D/$name.log"
  pkill -x dbpat; sleep 1
done
for p in $(pgrep -f "Xvfb :5[7]"); do kill $p; done
