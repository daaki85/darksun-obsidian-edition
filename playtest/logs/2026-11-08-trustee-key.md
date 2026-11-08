# 2026-11-08: the Trustee's key, and the dice log's turns after a fight

Build: obsidian-edition after "Dice log: no turn, and no thief's hiding rolled, when the leader
changes just after a fight". In DOSBox.

## Turns and hiding in a real fight (the leader fix)
From `pens-after-scar` (`toalarm.sh`, Cilla a 12th-level thief in memory; it stopped at (1832,
856): the walk arrow at (240, 160) took the party in; `restalarm.sh`: 5 rests, Kurzak's call, the
alarm). The fights' turns were logged ("K'ratchek's turn", "Cilla's turn") and Cilla's hiding rolled
on her turn ("Cilla hides in shadows: d100 = 35, needs 95 or less ... -> hidden", then move silently).
The alarm sent wave after wave with `fight_on` 0 only a moment between, so the leader change just
after a fight wasn't tried in play; the unit test `test_no_turn_out_of_a_fight` covers it. Outside a
fight (`pens-after-arena`), Cilla made leader on the inventory screen: whose turn read 3, and the dice
log printed nothing.

## The Trustee's key
From `pens-after-arena` (Cilla a 12th-level thief in memory): `follow.py 29` to Kurzak's stop, three
clicks at screen (176, 178) past him, `route.py`; Cilla made leader. The Trustee walks his rounds
fast; caught with the eye (it pauses the game) when near (`catch` scripts in the work folder).
- Talked to from about 5 squares: his menu had no "(PICK THE TRUSTEE'S POCKETS)".
- Talked to from 1-2 squares: the line was there. Script 146: offered only when the one talking is
  within 4 squares (its range command < 4), the key isn't stolen (flag 55 0) and the one talking is
  a thief (the class flags' thief bit).
- Picked: "Cilla tries to pick pockets: d100 = 86, needs 95 or less -> success", "You find a key!";
  Goodbye: "Cilla receives 250 experience points!" (XP: Cilla +83, three classes). The key (item 115,
  Slavepen key, picture 2161) was in Cilla's backpack, cell 14 (the first), and the Trustee carried
  nothing: the GIVE at the script's 0ABh worked. Its icon is a faint grey key on the grey cell,
  near invisible at the game's size; the bar names it on hover.

Not saved (memory edits).
