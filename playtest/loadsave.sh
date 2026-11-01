#!/bin/sh
# loadsave.sh NAME: start the game (start.sh, or start_recomp.sh with PT_TARGET=recomp) with the save in saves/NAME copied into the game
# folder (as slot 1), and load it: the title screens clicked past, LOAD SAVED GAME (170, 109), the
# first slot (100, 46), LOAD (253, 46). Prints the state once loaded.
. "$(dirname "$0")/env.sh"
[ -d "$PT/saves/$1" ] || { echo "no save $PT/saves/$1"; exit 1; }
# A set is SAVE01.SAV, CHARSAVE.GFF and DARKSAVE.GFF: LOAD copies DARKSAVE.GFF (the entities'
# timers, ETME, as saved) over DARKRUN.GFF, and a fresh install has no DARKSAVE.GFF, so the load
# failed there ("DARKSAVE.GFF to DARKRUN.GFF failed", DARKRUN.GFF left empty; 2026-11-01).
cp "$PT/saves/$1"/SAVE01.SAV "$PT/saves/$1"/CHARSAVE.GFF "$PT/saves/$1"/DARKSAVE.GFF "$GAME/"
if [ "$TARGET" = recomp ]; then sh "$PT/start_recomp.sh" | tail -1; sleep 6; else sh "$PT/start.sh" | tail -1; sleep 12; fi
W=$(timeout 10 xdotool search $WINQ | head -1)
timeout 5 xdotool windowmove $W 0 0; timeout 5 xdotool mousemove 160 120; sleep 0.3
timeout 5 xdotool click 1; sleep 1; timeout 5 xdotool click 1; sleep 12
timeout 15 python3 "$PT/click.py" 170 109 >/dev/null; sleep 4
timeout 15 python3 "$PT/click.py" 100 46 >/dev/null; sleep 1
timeout 15 python3 "$PT/click.py" 253 46 >/dev/null; sleep 12
timeout 10 python3 "$PT/state.py"
