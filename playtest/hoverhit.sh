#!/bin/sh
# hoverhit.sh C [attack]: the chance to hit under the pointer against the swing itself. On a party member's turn in a fight: the pointer moved onto enemy combatant C's figure (the walk arrow, or with "attack" the attack pointer, which shoots), the label the Loader floats over it read back (hoverlabel.py), then a left click there and the dice log's lines for the attack that follows (its "needs N+").
# The enemy must be on the screen with nothing in front of it (foepos.py lists the places; drag the
# view with scroll.py, not by the screen's edge). A waiting message is clicked away first. With the
# walk arrow the member walks up and fights hand to hand; never save after a test fight's edits.
. "$(dirname "$0")/env.sh"
if sh "$PT/msgbox.sh"; then sh "$PT/boxclick.sh"; sleep 2; fi
timeout 20 python3 "$PT/state.py"
timeout 40 python3 "$PT/pointer.py" ${2:-walk} 250 100 | tail -1
timeout 40 python3 "$PT/hoverlabel.py" foe $1
before=$(wc -l < "$WORK/dice.txt")
timeout 5 xdotool mousedown 1; sleep 0.12; timeout 5 xdotool mouseup 1
sleep ${HOVERHIT_WAIT:-6}
tail -n +$((before + 1)) "$WORK/dice.txt" | grep -A1 -E " attacks | shoots | hits |AC of |Message" | head -${HOVERHIT_LINES:-12}
timeout 20 python3 "$PT/state.py"
