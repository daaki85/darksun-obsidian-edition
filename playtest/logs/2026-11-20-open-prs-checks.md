# In-game checks for PRs #136, #140, #141 (2026-11-20)

Build: all seven open PRs (#135-#141) merged locally onto origin/obsidian-edition 0fbf97d
(local branch local-seven-combined, abdff05; CHANGELOG conflicts joined). DSCLOG.EXE matches a
fresh nasm build; buildcheck.py OK. Save: fountain-user. Autosave and quick save off (memory edits).

## #140: round counting (fountain-user's ambush)

1. `dismiss.sh`: the ambush, `Round 1: Lex 33, Guard 27, ...` (ten combatants, while `foeset.py`
   lists 30 non-party combatants on the map, most of them not in the fight: the stale tie-breaks
   the PR is about). `symread.py initiative_fight initiative_round`: fight 1, round 1.
2. Every foe held (`foeset.py C eff=34`), `passn.sh 8`: `Round 2`, `Round 3`, each order complete,
   no `?` rows.
3. The whole party held too (`addeffect.py N 34`, untimed), Lex's turn passed: the game played
   rounds in a blink (the helper's round counter went 3 -> 373 in about two seconds). The dice log:
   `(58 rolls came too fast to record)` twice, then **`Rounds 232-383 go by at once`** and
   `Round 384: ...`. The helper's counter read 384, so round 384 is right, but rounds 4-231 are
   missing from the count: it should say `Rounds 4-383`.
4. Again with a scratch `burst.py` (holds the party, frees one member when the turn passes): the
   turn never "passed" (`whose_turn` stays the same through the blink), so it ran until freed by
   hand: `Rounds 1281-1361 go by at once`, `Round 1362`; the helper said 1362. Rounds 385-1280 were
   lost the same way, again after "rolls came too fast to record".
   Cause: when the ring overruns, the older tie-break entries are dropped, and
   `initiative_lines` takes the first skipped round from the oldest entry left
   (`first = max(same_fight[0].number, self._round + 1)`). In the same fight it should be
   `self._round + 1`. The base build would have been wrong here too, but the PR's helper fields make
   the right answer available.
5. The panel's header read `Round 1362: Sene...`; the `ROUNDS ... SKIPPED` row had scrolled off
   (the mouse wheel through xdotool didn't scroll the panel).

## #141: spell recasts

1. `spellsetup.py 0=9 29` (Haste), on Lex's turn U, LEVEL to 3, Haste, a click on Jenna: one cast
   hasted all four (`Hasted on Lex`, `Lex gives Hasted to Jenna, Seneca`, `... to Ester`), each with
   the Loader's system shock roll and a year's ageing.
2. Haste again on Lex's next turn: `Lex gives Hasted to Lex, Jenna, in place of the ones they had`
   and `... to Ester, Seneca, in place of ...`: the recast is reported (the effect records looked the
   same before and after: spell 29, effect 22). **No ageing and no system shock on the recast.**
3. Four more rounds and the fight's end: no other `in place of` line (no false reports).
4. Not tried: an area change or a rest with a timed effect running (the false-report risk).

## #136: bulk loot

After `fightout.sh` (the fight's 1368 rounds in its tally, from the holds above):

1. Pehtucl's body (thing 151), Shift+T: `Lex takes Slavepen key, Grapes, Guava (4), Obsidian
   Bloodwrath +1`, `Ester takes Bone Brgnd.Chst Armor, ... Ring/Protection +1, Leather Shield`,
   the body empty, `carried.py` shows every item in the packs, window shut (5E6h 9999).
2. A guard's body (146), Shift+T: `Ester takes item 9999`, `Plain weapons left: Wooden Club (2)`;
   opened again, T: `Ester takes Wooden Club (2)`, the body empty.
3. The next body (147), T: Ester to a full pack, `Seneca takes Leather Chest Armor`, `No room in
   the backpacks for: Wooden Arrows`; then bodies 148-150: `The party's backpacks are full:
   nothing taken.` All four packs at 12 of 12; the game's free lists fine (`ring.Items`: things
   used 58, spare things and items).
4. Not from the PR: a body's purse-like thing (type 60, name number 9999, value 25 or 50) is named
   `item 9999` in the loot line.
5. The rollback path (a write failing mid-loot) can't be made to happen in play; the PR's unit tests
   cover it.

No save was made. Water: no new area.
