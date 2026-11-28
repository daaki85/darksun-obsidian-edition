#!/bin/sh
# ravload_recomp.sh NAME [FOLDER]: ravload.sh's run on Dark Sun Recompiled ($DSUN, its build/ds2o: Wake of
# the Ravager with the mod) instead of DOSBox, for comparing the two. FOLDER (default $WORK/ravr) is a copy of
# $WORK/rav (the big files linked) with the save in saves/NAME as slot 1, its sheets widened as the Loader
# does; the program runs as the Loader starts it (--game FOLDER --cd the mod's dos folder: its patched copy,
# DSCLOG2 and the CD on F:), its window 320x240 at 0,0, its pid in $WORK/dsun.pid, its log $WORK/dsun.log.
# Shift skips the intro, then LOAD SAVED GAME (game 159,110), the first slot (127,46), LOAD (252,47) through
# ravclick.py (it reads the pointer in the program's memory as in DOSBox's). Kills only its own earlier
# program ($WORK/dsun.pid). About 60 s.
. "$(dirname "$0")/env.sh"
F=${2:-$WORK/ravr}
[ -x "$DSUN" ] || { echo "no program at $DSUN (DSUN=... names it)"; exit 1; }
B=${DSUN_BUILD:-$(cd "$(dirname "$DSUN")/.." && pwd)/ds2o}   # (the program's build/ds2o: its repository's, beside build/cmake)
[ -f "$B/image.bin" ] || { echo "no $B/image.bin (tools/build_mod.sh <mod> ravager in the program's repository; DSUN_BUILD names another)"; exit 1; }
[ -d "$PT/saves/$1" ] || { echo "no save $PT/saves/$1"; exit 1; }
[ -f "$WORK/rav/DSUN.EXE" ] || { echo "no $WORK/rav (setup_ravager.sh, and ravstart.sh once: the Loader's copies)"; exit 1; }
[ -f "$WORK/dsun.pid" ] && kill -9 "$(cat "$WORK/dsun.pid")" 2>/dev/null; sleep 1
if [ ! -d "$F" ]; then     # (the big files linked, the rest copied: the game writes its saves and roster)
  mkdir -p "$F"; for f in "$WORK/rav"/*; do
    case "$(basename "$f")" in game.gog|MUSIC|cd|*.FLI|*.fli|__support) ln -s "$f" "$F/";; *) cp -r "$f" "$F/";; esac; done
fi
cp "$PT/saves/$1"/SAVE01.SAV "$PT/saves/$1"/CHARSAVE.GFF "$PT/saves/$1"/DARKSAVE.GFF "$F/"
rm -f "$F"/*.42H
(cd "$REPO/obsidian-edition" && python3 -c "
import sys; from dsloader import ravager; ravager.widen_files(sys.argv[1])" "$F") || exit 1
pgrep -x Xvfb >/dev/null || { setsid nohup Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 & sleep 2; }
cd "$F" && (SDL_AUDIODRIVER=dummy setsid "$DSUN" --game "$F" --build "$B" --cd "$REPO/obsidian-edition/dos" > "$WORK/dsun.log" 2>&1 < /dev/null & echo $! > "$WORK/dsun.pid")
for i in $(seq 1 30); do W=$(timeout 5 xdotool search --name Recompiled | head -1); [ -n "$W" ] && break; sleep 1; done
[ -z "$W" ] && { echo "no window (see $WORK/dsun.log)"; exit 1; }
grep -q "Obsidian Edition" "$WORK/dsun.log" || { echo "not the mod's build: $(grep -m1 'Dark Sun' "$WORK/dsun.log")"; exit 1; }
timeout 5 xdotool windowmove $W 0 0; timeout 5 xdotool windowsize $W 320 240; sleep 2
for t in 1 2 3; do xdotool keydown --window "$W" Shift_L; sleep 1; xdotool keyup --window "$W" Shift_L; sleep 3; done
import -window "$W" "$WORK/ravr-menu.png"
cd "$PT"
python3 ravclick.py 159 110 left "$(cat "$WORK/dsun.pid")" >/dev/null; sleep 4
python3 ravclick.py 127 46 left "$(cat "$WORK/dsun.pid")" >/dev/null; sleep 1
python3 ravclick.py 252 47 left "$(cat "$WORK/dsun.pid")" >/dev/null; sleep 15
import -window "$W" "$WORK/ravr-loaded.png"; echo "pid $(cat "$WORK/dsun.pid"), window $W: loaded $1: $WORK/ravr-loaded.png"
