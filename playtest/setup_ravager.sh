#!/bin/sh
# setup_ravager.sh: Wake of the Ravager, the sequel, for comparing with Shattered Lands (its code,
# data and README), in $RAV (default $WORK/rav): the GOG installer from the owner's Google Drive
# ("Dark Sun Install Files", setup_dark_sun_2_wake_of_the_ravager_1.1_(28043).exe, 208 MB), file id
# below, extracted with innoextract. Not played: nothing in the kit runs it.
. "$(dirname "$0")/env.sh"
RAV=${RAV:-$WORK/rav}
[ -f "$RAV/DSUN.EXE" ] && { echo "already there: $RAV"; exit 0; }
mkdir -p "$WORK/dl" "$RAV"
curl -sSL -o "$WORK/dl/rav.exe" "https://drive.usercontent.google.com/download?id=1DVgifgu6eCYMQNr9wKvLTvisJEyAMbho&export=download&confirm=t"
cd "$RAV" && innoextract -s -d . "$WORK/dl/rav.exe" && ls DSUN.EXE README.TXT
