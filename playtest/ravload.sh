#!/bin/sh
# ravload.sh NAME [FOLDER]: Wake of the Ravager from the save in saves/NAME (SAVE01.SAV, CHARSAVE.GFF,
# DARKSAVE.GFF copied into FOLDER, default $WORK/rav, as slot 1), started as the Loader starts it
# (RAV_LOADER=1; RAV_SKIP passes through for a control's copy): ravstart.sh to the title menu
# (RAV_MENU=1), a click to take the mouse, LOAD SAVED GAME (game 159,110), the first slot (127,46),
# LOAD (252,47). Kills nothing: stop an earlier DOSBox first. About 70 s.
. "$(dirname "$0")/env.sh"
F=${2:-$WORK/rav}
[ -d "$PT/saves/$1" ] || { echo "no save $PT/saves/$1"; exit 1; }
cp "$PT/saves/$1"/SAVE01.SAV "$PT/saves/$1"/CHARSAVE.GFF "$PT/saves/$1"/DARKSAVE.GFF "$F/"
RAV_LOADER=1 RAV_MENU=1 sh "$PT/ravstart.sh" "$F" | tail -1 || exit 1
W=$(xdotool search --pid "$(cat "$WORK/rav.pid")" | tail -1)
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 1
cd "$PT"
python3 ravclick.py 159 110 >/dev/null; sleep 4
python3 ravclick.py 127 46 >/dev/null; sleep 1
python3 ravclick.py 252 47 >/dev/null; sleep 15
import -window "$W" "$WORK/rav-loaded.png"; echo "loaded $1: $WORK/rav-loaded.png"
