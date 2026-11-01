# env.sh: sourced by every playtest shell tool. PT the kit, REPO the repository, WORK the scratch
# folder (screenshots, logs: never committed), GAME the extracted GOG game. Override with
# PLAYTEST_WORK and DS_GAME. The X display the game runs on is :55 (Xvfb).
PT=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$PT/.." && pwd)
WORK=${PLAYTEST_WORK:-/tmp/playtest}; GAME=${DS_GAME:-$WORK/inst}
export PT REPO WORK GAME DISPLAY=:55; mkdir -p "$WORK"
