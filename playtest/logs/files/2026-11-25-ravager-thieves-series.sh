#!/bin/sh
# the controls and the Assassin's runs: Tctl2 (Thieves as in AD&D off), A1 (Seneca a human thief 3 Assassin, a
# test edit), Actl (the same, the kits off), each tried up to twice for a backstab
S=$(dirname "$0")
for run in "Tctl2 0x100 -" "A1 0 1 2 1 17" "Actl 0x10000 1 2 1 17"; do
  set -- $run; T=$1; O=$2; shift 2; E="$*"; [ "$E" = "-" ] && E=
  sh $S/2026-11-25-ravager-thieves-run.sh $T $O "$E" | tail -1 > /tmp/playtest/t-$T.res
  grep -q "no backstab" /tmp/playtest/t-$T.res && sh $S/2026-11-25-ravager-thieves-run.sh ${T}b $O "$E" | tail -1 >> /tmp/playtest/t-$T.res
  cat /tmp/playtest/t-$T.res
done
echo series done
