#!/bin/sh
# setup_ravager.sh: Wake of the Ravager, the sequel, for comparing with Shattered Lands (its code,
# data and README), in $RAV (default $WORK/rav): the owner's GOG installer, extracted with
# innoextract. Never downloaded from a public link: put it at $WORK/dl/rav.exe by hand first (or
# name it in $PT_RAV_INSTALLER). Not played: nothing in the kit runs it.
. "$(dirname "$0")/env.sh"
RAV=${RAV:-$WORK/rav}
[ -f "$RAV/DSUN.EXE" ] && { echo "already there: $RAV"; exit 0; }
mkdir -p "$WORK/dl" "$RAV"
RI=${PT_RAV_INSTALLER:-$WORK/dl/rav.exe}
[ -s "$RI" ] || { echo "no installer at $RI: put your own copy of the GOG installer there (never a public link)"; exit 1; }
cd "$RAV" && innoextract -s -d . "$RI" && ls DSUN.EXE README.TXT
