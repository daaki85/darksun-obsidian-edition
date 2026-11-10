#!/bin/sh
# setup_game.sh: the game for testing, in $GAME: the GOG installer (on the owner's Google Drive,
# file id below; fetch it through the Drive connector, or with curl while the file is shared) and
# innoextract. Needs: dosbox Xvfb xdotool imagemagick innoextract (all apt packages).
. "$(dirname "$0")/env.sh"
[ -f "$GAME/DSUN.EXE" ] && { echo "already there: $GAME"; exit 0; }
mkdir -p "$WORK/dl" "$GAME"
curl -sSL -o "$WORK/dl/sl.exe" "https://drive.usercontent.google.com/download?id=1mANnoCbl50lPtfYGABsZwZkEw7IZUj4P&export=download&confirm=t"
cd "$GAME" && innoextract -s -d . "$WORK/dl/sl.exe" && ls DSUN.EXE GPLDATA.GFF
# GOG's install copies __support/save (the starting DARKSAVE.GFF, CHARSAVE.GFF) into cloud_saves, which
# its DOSBox overlays on C:; innoextract doesn't, and Linux's DOSBox 0.74-3 has no overlay mount: put
# them in the game folder, or the game quits at START GAME ("DARKSAVE.GFF to DARKRUN.GFF failed",
# 2026-11-10). (A cloud_saves folder would make the Loader's config ask for the overlay: none here.)
for f in "$GAME"/__support/save/*; do [ -f "$GAME/$(basename "$f")" ] || cp "$f" "$GAME/"; done
