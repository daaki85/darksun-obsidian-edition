# 2026-11-10: the staff sling's stinkpots

The build under test is commit fa23dbc. `buildcheck.py` OK. Memory edits only; no game was saved.

From `fountain-user`:
- Lex's missile-slot bow (item 36) was made the game's Leather Staff Sling (type 0) with `/tmp/playtest/setitem.py 36 0`, a scratch script (the record from SEGOBJEX, link, flags and slot kept, +08h 270Fh). Type 0's record in memory read sides 3: the rule's 1d3.
- Every foe was held (`foeset.py C eff=34`). Then the speech box was clicked and `passuntil.sh 0`.
- **The shot:** `pointer.py attack`, then a click on the foe's figure. The figure is about 10 pixels above its feet: the place at DS:669Dh + 32 x combatant less the camera. A click beside it showed the red "can't" sign.

The dice log:
```
Lex attacks Templar with Leather Staff Sling (1d3): d20 = 11, needs 10+ (55%), hits AC 3, target AC 4 -> HIT
    Paralyzed: hit automatically, for normal damage (AD&D's held target)
  Lex hits Templar for 3: 1d3 = [3]
    Lex's stinkpot: Templar is nauseated, no saving throw (helpless), -2 to hit for 1d3+1 = 2 + 1 = 3 rounds
Lex gives Nauseated to Templar: -2 to hit (a staff sling's stinkpot)
```
`effects.py`: "owner 25, id 75, secs 180 | Nauseated (3 rounds)".

The Templar was freed (`addeffect.py del 25 34`). Lex's next shot rolled its save:
```
Templar's saving throw vs a stinkpot from Lex (paralysis/poison/death): d20 = 11 +1 Ring of Protection = 12, needs 7 (75% to save) -> saved
```

The nauseated Templar's own attack, two turns later:
```
Templar attacks Jenna with Obsidian Bloodwrath +1 (1d8+1): d20 = 1 (natural 1), needs 16+ (25%), hits AC 18, target AC 3 -> miss
    THAC0 18, -2 Nauseated, +1 weapon = 19
```
By then the effect showed 60 s, "1 round" left: it counts down.

Not looked at: the effect's NAUSEATED entry on the Effects screen. That screen shows party members, and the effect was only on a foe. Its name and icon are covered by `test_stinkpots`.
