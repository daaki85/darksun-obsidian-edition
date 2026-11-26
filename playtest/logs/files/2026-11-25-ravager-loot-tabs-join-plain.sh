#!/bin/sh
# 2026-11-25-ravager-loot-tabs-join-plain.sh (run from playtest/): the control with no mod at all. ravJ5p (a fresh
# copy of rav, thrown away after), ravager-after-ambush's files copied in, the sequel started as GOG's (ravstart.sh
# without RAV_LOADER: the game's own DSUN.EXE, no DSCLOG2, no patches, no Loader), then ravload.sh's clicks (LOAD
# SAVED GAME, the first slot, LOAD). Its window id in $WORK/j5w.
PT=$(cd "$(dirname "$0")/../.." && pwd); cd "$PT"; export DISPLAY=:55 PLAYTEST_WORK=/tmp/playtest
W0=/tmp/playtest; F=$W0/ravJ5p
rm -rf $F; cp -a $W0/rav $F
rm -f $F/SAVQ*.SAV
cp saves/ravager-after-ambush/SAVE01.SAV saves/ravager-after-ambush/CHARSAVE.GFF saves/ravager-after-ambush/DARKSAVE.GFF $F/
RAV_STDOUT=1 RAV_MENU=1 timeout 200 sh ravstart.sh $F | tail -1
W=$(xdotool search --pid "$(cat $W0/rav.pid)" | tail -1); echo $W > $W0/j5w
xdotool mousemove --window "$W" 400 200; sleep 0.3; xdotool click --window "$W" 1; sleep 1
python3 ravclick.py 159 110 >/dev/null; sleep 4
python3 ravclick.py 127 46 >/dev/null; sleep 1
python3 ravclick.py 252 47 >/dev/null; sleep 15
import -window "$W" "$W0/j5p-loaded.png"; echo "loaded: $W0/j5p-loaded.png"
