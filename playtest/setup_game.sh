#!/bin/sh
# setup_game.sh: the game for testing, in $GAME: the GOG installer extracted with innoextract.
# The installer is the owner's own copy and is never downloaded from a public link (the repository
# is public; sharing it would be piracy): put it at $WORK/dl/sl.exe by hand first (or name it in
# $PT_SL_INSTALLER). Needs: dosbox Xvfb xdotool imagemagick innoextract (all apt packages).
. "$(dirname "$0")/env.sh"
[ -f "$GAME/DSUN.EXE" ] && { echo "already there: $GAME"; exit 0; }
mkdir -p "$WORK/dl" "$GAME"
SL=${PT_SL_INSTALLER:-$WORK/dl/sl.exe}
[ -s "$SL" ] || { echo "no installer at $SL: put your own copy of the GOG installer there (never a public link)"; exit 1; }
cd "$GAME" && innoextract -s -d . "$SL" && ls DSUN.EXE GPLDATA.GFF
# GOG's install copies __support/save (the starting DARKSAVE.GFF, CHARSAVE.GFF) into cloud_saves, which
# its DOSBox overlays on C:; innoextract doesn't, and Linux's DOSBox 0.74-3 has no overlay mount: put
# them in the game folder, or the game quits at START GAME ("DARKSAVE.GFF to DARKRUN.GFF failed",
# 2026-11-10). (A cloud_saves folder would make the Loader's config ask for the overlay: none here.)
for f in "$GAME"/__support/save/*; do [ -f "$GAME/$(basename "$f")" ] || cp "$f" "$GAME/"; done
