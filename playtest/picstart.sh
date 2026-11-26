#!/bin/sh
# picstart.sh PICTURE [SCALE] [OUT_DIR]: the game started with one of the Loader's pictures (plain,
# scanlines, tv, sharp) in a window SCALE times the game's (default 3), NOT the kit's 320x240 start:
# pens-after-arena loaded by the pointer (click.py), then the window's size, pointer checks
# (picmove.py: the hand moved SCALE screen pixels a game pixel), a grab of the window
# (OUT_DIR/PICTURE-SCALE.png) and DOSBox's log. It ends DOSBox and puts window_scale 1 and the plain
# picture back in settings.json, so the next start.sh is the kit's own. Run it under the DOSBox lock.
# The screen (Xvfb :55) is 1024x768: scale 4 doesn't fit it (picpattern.sh shows that one).
. "$(dirname "$0")/env.sh"
MODE=$1; SCALE=${2:-3}; OUT=${3:-$WORK/pic}; mkdir -p "$OUT"
pgrep -x Xvfb >/dev/null || (Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 1
for p in $(pgrep -f "^python3 -u -m dsloade[r]"); do kill $p; done; pkill -9 -x dosbox; sleep 1
cp "$PT/saves/pens-after-arena"/SAVE01.SAV "$PT/saves/pens-after-arena"/CHARSAVE.GFF "$PT/saves/pens-after-arena"/DARKSAVE.GFF "$GAME/"
settings() {  # settings SCALE PICTURE: settings.json's window and picture
  (cd "$REPO/obsidian-edition" && python3 -c "
from dsloader import launch
s = launch.load_settings(); s['game_dir'] = '$GAME'; s['window_scale'] = $1; s['picture'] = '$2'; s['fullscreen'] = False
launch.save_settings(s)")
}
settings $SCALE $MODE
cd "$REPO/obsidian-edition" && python3 -c "
from dsloader import launch
print('problem:', launch.prepare_patched_game('$GAME'))
print(launch.write_conf('$GAME'))"
settings 1 plain   # (back at once: the conf is written, and a run cut short leaves the kit's settings)
sed -n '1,/autoexec/p' "$REPO/obsidian-edition/dosbox_dicelog.conf"
cd "$GAME/DOSBOX" && (SDL_AUDIODRIVER=disk SDL_DISKAUDIOFILE=/dev/null setsid dosbox -conf ../__support/app/dosbox_darksun.conf -conf "$REPO/obsidian-edition/dosbox_dicelog.conf" >"$OUT/$MODE-$SCALE-dosbox.log" 2>&1 < /dev/null &)
sleep 14
W=$(timeout 10 xdotool search $WINQ | head -1); echo "window $W"
timeout 5 xdotool windowmove $W 0 0; timeout 5 xdotool mousemove $((160*SCALE)) $((120*SCALE)); sleep 0.3
timeout 5 xdotool click 1; sleep 1; timeout 5 xdotool click 1; sleep 12
timeout 5 xdotool getwindowgeometry $W
timeout 20 python3 "$PT/click.py" 170 109; sleep 4
timeout 20 python3 "$PT/click.py" 100 46; sleep 1
timeout 20 python3 "$PT/click.py" 253 46; sleep 12
timeout 10 python3 "$PT/state.py"
echo "-- pointer"
timeout 20 python3 "$PT/click.py" 100 60 none
timeout 20 python3 "$PT/picmove.py" $((30*SCALE)) 0
timeout 20 python3 "$PT/picmove.py" 0 $((30*SCALE))
timeout 20 python3 "$PT/picmove.py" -$((20*SCALE)) -$((20*SCALE))
timeout 20 python3 "$PT/click.py" 250 150 none
timeout 20 python3 "$PT/click.py" 40 30 none
sleep 0.5
timeout 10 import -window $W "$OUT/$MODE-$SCALE.png"; identify "$OUT/$MODE-$SCALE.png"
echo "-- dosbox log"; cat "$OUT/$MODE-$SCALE-dosbox.log"
pkill -9 -x dosbox
echo "done: $OUT/$MODE-$SCALE.png"
