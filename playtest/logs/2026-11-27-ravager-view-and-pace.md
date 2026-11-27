# 2026-11-27: Wake of the Ravager, the view in fights, the whole party in view, steady pace

Under test: DSCLOG2's sites 230-234 (branch `claude/ravager-view-and-pace`), ported from Codex's unmerged
`codex/ravager-map-controls`. Save `ravager-after-ambush` (`ravload.sh`), the Loader's way, with
`ravdice.py` attached; the thieves' fight in Tyr (arrow keys Up 8, Right 40, `ravgo.py x 1850 y 1237`,
answer 2, Space) played with `ravfight.py tabfight`.

## Before (the build on obsidian-edition 5078a0d5)

- Loaded: the party one figure (Thy'rokh). After the thieves' fight: one figure again.
- The view, sampled every 50 ms (DS:1408h, 140Ah, a scratch logger): on turn 23 (a thief walking, on
  screen) it moved 7 times in 1.5 s, in steps of 16 and 32, while he walked.
- While there: the combat log panel (L), M, U, I, F5 (`Quick save: "Quick - Day 1, 00:05"`), F9 (the
  sequel's LOAD window with it chosen) and Enter in it (loaded: `ravquick.py` greq read 1), Tab (ring,
  the view panned, "Chosen with Tab: Thief ... Enter attacks it"), Enter (the attack), the chance to hit
  under the pointer ("Backstab 10+ (55%)" over a thug), R (the squares off and on), the fight's tally
  ("Fight over: 4 rounds, 4 kills; ...") and the autosave after it all worked.

## After

- Loaded: the whole party on the map. 6 gathered it and it stayed so; 5 spread it; walking spread.
- The same fight, the figure's feet logged with the view: on turn 23 the thief walked from 104 to 224
  below the view's top with the view still, which stepped only once his feet were off the screen (208,
  224); on turn 26 a walker crossed 152 to 216 across with the view still. The view still scrolls to
  whoever's turn it is at a turn's start (21341h), as the game does.
- Steady pace: DSCLOG2's counters (segment from INT F5h's vector, offsets 9A81h on from `nasm -l`): 2624
  steps run, 1303 lost, 181 frames left undrawn over the walk and fight. Nothing seen drawn wrong.
- `DSUN_SL`/`DSUN_WOTR` start-up tests, test_ravager, test_ravkitpages, test_dsclog2_room: passed.

A second fight was lost: the dice log had died with the first DOSBox (killed for the restart), so Tab
did nothing and `ravfight.py tabfight` never attacked. Restart `ravdice.py` after every `ravload.sh`.

Water: none new (Tyr's street, as before).
