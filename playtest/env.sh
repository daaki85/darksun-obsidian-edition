# env.sh: sourced by every playtest shell tool. PT the kit, REPO the repository, WORK the scratch
# folder (screenshots, logs: never committed), GAME the extracted GOG game. Override with
# PLAYTEST_WORK and DS_GAME. The X display the game runs on is :55 (Xvfb).
PT=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$PT/.." && pwd)
WORK=${PLAYTEST_WORK:-/tmp/playtest}; GAME=${DS_GAME:-$WORK/inst}
# PT_TARGET=dosbox (default) or recomp (Dark Sun Recompiled, $DSUN): which program runs the game.
# WINQ finds its window for xdotool; grab320 WINDOW OUT.png takes a 320x240 grab of it (DOSBox's
# window is that size; the program's is resized to it by start_recomp.sh).
TARGET=${PT_TARGET:-dosbox}; DSUN=${DSUN:-/home/user/darksun-recompiled/build/cmake/dsun}
if [ "$TARGET" = recomp ]; then WINQ="--name Dark Sun Recompiled"; else WINQ="--class dosbox"; fi
export PT REPO WORK GAME TARGET DSUN WINQ DISPLAY=:55; mkdir -p "$WORK"
