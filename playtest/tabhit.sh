#!/bin/sh
# tabhit.sh [TABS [nohit]]: the chance to hit before the swing against the swing itself. On a party
# member's turn in a fight: Tab TABS times (1: the nearest enemy), the dice log's "Chosen with Tab"
# line (the Loader's prediction, dsloader/hitchance.py), then Return and the dice log's lines for
# the attack that follows (its "needs N+"). With "nohit", no Return: only the choice (and
# hitcheck.py for what the number is made of). A waiting message is clicked away first.
. "$(dirname "$0")/env.sh"
W=$(timeout 5 xdotool search $WINQ | head -1)
if sh "$PT/msgbox.sh"; then sh "$PT/boxclick.sh"; sleep 2; fi
f=$(timeout 20 python3 "$PT/state.py"); echo "$f"
before=$(wc -l < "$WORK/dice.txt")
for i in $(seq 1 ${1:-1}); do timeout 5 xdotool key --window $W Tab; sleep 1; done
sleep 1
tail -n +$((before + 1)) "$WORK/dice.txt" | grep "Chosen with Tab" | tail -1
[ "$2" = nohit ] && exit 0
timeout 20 python3 "$PT/hitcheck.py" | grep -v "^  "
before=$(wc -l < "$WORK/dice.txt")
timeout 5 xdotool key --window $W Return; sleep ${TABHIT_WAIT:-6}
tail -n +$((before + 1)) "$WORK/dice.txt" | grep -A1 -E " attacks | hits |AC of " | head -${TABHIT_LINES:-12}
timeout 20 python3 "$PT/state.py"
