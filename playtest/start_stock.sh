#!/bin/sh
# start_stock.sh [GAMEDIR]: the stock game (no Loader, no dice log) in plain DOSBox on :55, from GAMEDIR
# (default $WORK/darkfix-inst: a copy of inst with OpenDS's darkfix applied by darkfix_apply.py). GOG's
# own dosbox_darksun.conf first (its SB IRQ 5 matches the install's SOUND.CFG: without it DSUN.EXE
# drops back to DOS at once), then a conf of ours: windowed 320x240 and the game started. The intro
# plays (Escape skips it); then the main menu, as loadsave.sh's clicks. Kills nothing but its own.
. "$(dirname "$0")/env.sh"
G=${1:-$WORK/darkfix-inst}
[ -f "$G/DSUN.EXE" ] || { echo "no game at $G"; exit 1; }
pgrep -x Xvfb >/dev/null || (setsid nohup Xvfb :55 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 1
cat > "$WORK/stock.conf" <<CONF
[sdl]
fullscreen=false
autolock=true
[render]
aspect=true
scaler=none
[cpu]
core=dynamic
cycles=fixed 35000
[dos]
ems=false
[autoexec]
@echo off
mount c "$G"
c:
dsun
exit
CONF
cd "$G/DOSBOX" && (SDL_AUDIODRIVER=disk SDL_DISKAUDIOFILE="$WORK/audio.raw" setsid dosbox -conf ../__support/app/dosbox_darksun.conf -conf "$WORK/stock.conf" >"$WORK/dosbox-stock.log" 2>&1 < /dev/null &)
sleep 12; W=$(timeout 10 xdotool search $WINQ | head -1); timeout 5 xdotool windowmove $W 0 0
echo "started $(pgrep -nx dosbox)"
