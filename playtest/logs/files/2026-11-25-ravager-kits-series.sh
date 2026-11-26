#!/bin/sh
# the kits' runs on the merged build: A (Justifier, fighter Ravager, dwarf Ghetto Fighter, half-elf Wilderness Avenger), B (Stalker, Myrmidon, half-elf Military Scout, mul Wild Fury)
K=$(dirname "$0")/2026-11-25-ravager-kits-run.sh
for run in "A1 0" "Actl1 0x10000"; do set -- $run; sh $K $1 $2 "r 2" "9,11 3 - 9" "17,9 1 2" "9,d 1 4"; done
for run in "B1 0" "Bctl1 0x10000"; do set -- $run; sh $K $1 $2 "r 1" "9,11 1 - 9" "17,9 2 4" "9,d 1 7"; done
echo fullseries done
