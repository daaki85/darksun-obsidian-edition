#!/bin/sh
# start.sh: Xvfb :55, the Loader's patched game in DOSBox as the Loader starts it (the repository's
# current code: rebuild = restart), and the Loader's dice log ($WORK/dice.txt). Kills any old ones.
# Then: topartyfight.sh for a new game. Check the build is in place before trusting what you see.
. "$(dirname "$0")/env.sh"
pgrep -x Xvfb >/dev/null || (Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 1
for p in $(pgrep -f "^python3 -u -m dsloade[r]"); do kill $p; done; pkill -9 -x dosbox; sleep 1
cd "$REPO/obsidian-edition" && python3 -c "
from dsloader import launch
s = launch.load_settings(); s['game_dir'] = '$GAME'; s['window_scale'] = 1; launch.save_settings(s)
print('problem:', launch.prepare_patched_game('$GAME'))
print(launch.write_conf('$GAME'))"
# PT_CYCLES: a test's own DOSBox speed (any number; the Options tab offers 20000 and 35000)
[ -n "$PT_CYCLES" ] && sed -i "s/^cycles=fixed .*/cycles=fixed $PT_CYCLES/" "$REPO/obsidian-edition/dosbox_dicelog.conf" && grep -n "^cycles" "$REPO/obsidian-edition/dosbox_dicelog.conf"
cd "$GAME/DOSBOX" && (SDL_AUDIODRIVER=disk SDL_DISKAUDIOFILE="${PT_AUDIO:-/dev/null}" setsid dosbox -conf ../__support/app/dosbox_darksun.conf -conf "$REPO/obsidian-edition/dosbox_dicelog.conf" >"$WORK/dosbox.log" 2>&1 < /dev/null &)
sleep 4; cd "$REPO/obsidian-edition" && (setsid nohup python3 -u -m dsloader dicelog > "$WORK/dice.txt" 2>&1 < /dev/null &)
echo started
