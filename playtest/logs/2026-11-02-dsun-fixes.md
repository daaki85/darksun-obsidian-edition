# In-game test: two DSUN.EXE fixes (2026-11-01)

## Under test (commit 3c3c388)
- DSCLOG's PROBE_WORN (INT 81h): an ability item (+0Fh FAh-FFh) counts only in a worn slot
  (7B8ABh); a gladiator's armour optimisation only with armour on (58F86h).
- Also: the game starts and runs with the new helper (smoke test).

## Log
- Smoke: pens-kurzak-door loads with the new helper; the running copy (dos/DSUNLOG.EXE) has
  both patches (58F86h cd8190909090, 7B8ABh cd819090).
- **Ability items, passed.** Gerakis's sling (missile slot, worn) given +0Fh FBh (DEX) and
  +0Eh 2 in memory; opening the inventory alone recounts nothing; picking the sling up and
  putting it back did: DEX 15 -> 17 (dice log "Gerakis's DEX 15 -> 17"). Moved to the first
  backpack cell (slot byte 14): DEX 17 -> 15. Sling put back, its bytes cleared.
- Learned: an item's +0Fh is also the spell the game casts on the wearer as it is put on
  (FAh-FFh the ability pseudo-spells): putting the sling on with FBh made a lasting DEX +2
  effect, kept in the item's byte 2 for taking it off; clearing the bytes while it was worn left
  that effect behind (DEX 17 after). An artefact of editing memory; worn, DEX rose by 2, not 4,
  so the effect and the item loop don't add up. Reloaded the save to be rid of it.
- Gladiator test, set up: no fight could be had in the pens (the main door's knock menu needs it
  closed; the fire ring isn't scripted), so a new game to the arena's first fight. Before it, in
  memory: Gerakis (#0, gladiator, arm, leg and chest armour) to 10th level; Cermak (#2, human,
  his second class gladiator, no armour) to 10th and the gladiator flag. Expected ACs (the
  Loader's count, the same rules): Gerakis 4 (6 less the bonus of 2), Cermak 6 (no bonus; the
  game before the fix: 4).
- **Gladiator: not seen in play.** The game works an AC out only for an attack. No fight could be
  had: in the pens the main door (objects 2145-2146, its "Take me to the Arena!" menu, 137:14CEh)
  answers nothing while open, and resting is at a fire ring, not found; a new game reached the
  arena gate (topartyfight.sh: "NO FIGHT"), and 60-odd clicks and walks between (488, 232) and
  (488, 264) over several game minutes never started the first bout (its start is GPL 2's entry
  at 1, run by MAS 42's code-111 trigger on object 2059 at 498,341, beyond the bone wall; case 1
  wants flag 5, which MAS 42 sets on loading). Flags can't be read in the arena. The inventory's
  AC and THAC0 (AC 6, THAC0 13) didn't follow the sheet's level raised in memory: no test there.
  The rule stays checked by the emulator tests only (WornTests, the Wall of Thorns gladiator).
- Smoke: the new helper ran the pens and the arena's opening show (the Rampager's fight, the
  Defiler killed) with no fault.
- All memory edits gone with the game (nothing saved).

## The gladiator in the inventory (2026-11-02, the user's suggestion)
- The inventory's AC line is the game's own and is worked out afresh from what is worn; read it
  after switching to another member and back (it was one change behind otherwise).
- Gerakis (gladiator), pens-kurzak-door, his level raised in memory:

| Wears | Level 3 | Level 10 |
|---|---|---|
| arm, leg and chest armour | 7 | 5 (the bonus of 2) |
| arm and leg armour | 8 | 6 (the bonus of 2) |
| no armour | 9 | 9 (no bonus: **the fix working**; before it, 7) |

- Armour put back; nothing saved.
- Found: with armour on, the game's AC is 1 worse than the Loader's `counted_ac` (7 against 6;
  9 and 9 with none): a follow-up for the Loader's count (the Look box, Wall of Thorns).
