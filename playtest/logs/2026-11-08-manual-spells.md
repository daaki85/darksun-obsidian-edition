# Play test: the spells "as the manual describes them" (2026-11-08)

Under test: the Obsidian Edition's SPELLS_MANUAL patches (gamepatch.py), switch `spells_manual` on
(settings: None = on, default). DOSBox, the Loader's patched game, dice log `$PLAYTEST_WORK/dice.txt`.


## Summary

| Spell | Expected | Seen | Verdict |
|---|---|---|---|
| Bestow Curse (104) | a save rolled | `Templar's saving throw vs Bestow Curse from Ester (spell): d20 = 1 (natural 1) -> failed` | OK |
| Blood Flow (108) | a save rolled | `Jenna's saving throw vs Blood Flow from Ester (spell): d20 = 1 (natural 1) -> failed` | OK |
| Flaming Sphere (14) | made save: no damage | `... -> saved: no damage (not 2)`; failed: `full damage, 8` | OK (the sphere struck the caster, not the guard clicked) |
| Solid Fog (51) | 1d3 + 1/level rounds | `lasts 11 rounds (caster level 9: ... = 9 + 2 from the dice; dice 1d3 = [2])`; effects `Stuck (11 rounds)` | OK |
| Minor Spell Turning (48) | 3 rounds/level | `Spell Turning (26 rounds)` a round after a level-9 cast | OK |
| MST, more than one spell | (asked) | two Cure Light Wounds at Lex, a round apart, both turned (`Ester regains 7 HP ...`); still on after; Blood Flow (4th) not turned | turns every 1st-3rd level spell for its whole time |
| Cause Fear (78) | 1d4 rounds | `lasts 1 round (caster level 9: 1 from the dice; dice 1d4 = [1])`; Templar's: `lasts 4 rounds (caster level 8: 4 from the dice ...)` | OK |
| Quicksand (134) | 1 round/level, no save | no save rolled (switch off: saves rolled); Stuck 1 round each, renewed every round while the quicksand lasts its own 5d3 rounds (rounds 1-11 here) | no save OK; the time change has no visible effect |
| Turn Pebble to Boulder (53) | 3d6+8 | `3d6 = [1 + 3 + 5] +8 = 17` | OK |
| Magical Stone (75) | 3d4 | three throws a casting, each `3d4` (7, 7, 10); switch off: three throws of `1d4` | each stone 3d4 = 9d4 a casting: too much |
| Ironskin (133) | charges = level | `charges None secs 0 / Ironskin (0 rounds)`, `Ironskin ends` at the next turn, no blow struck; switch off: `Ironskin (6 charges)` | BROKEN: 0 charges |
| Stinking Cloud (22) | 1d4+1 rounds | `lasts 4 rounds (caster level 9: 3 from the dice + 1 more; dice 1d4 = [3])` | OK |
| Chaos (56), INT 22 non-warrior | normal save | `d20 = 6 +1 ... = 10, needs 12 (65% to save) -> failed` | OK |
| Chaos, INT 12 non-warrior | no save | `none allowed (cannot save) -> failed` | OK |
| Free Action (117) | frees Stuck; ends Paralyzed, Slowed | `Stuck ends on Jenna`; `Slowed ends on Ester`; `Paralyzed ends on Lex` | OK |
| Remove Paralysis (105) | still works | `Paralyzed ends on Seneca` | OK |
| Minute Meteors (33) | min(level,10)d4, one roll; to-hit? | `9d4 = [2 + 1 + 4 + 1 + 4 + 3 + 4 + 1 + 2] = 22 (... caster level ... 9)`; no to-hit line | the caster's level IS counted (level 9: 9 dice); no to-hit |

## Steps

- Settings: `spells_manual` reads None (on).
- Build check: DOSBox runs `d:\dsunlog.exe` (dos/DSUNLOG.EXE, the patched copy). Spell records read
  from game memory (`gd.spell_record`) equal DSUNLOG.EXE's for every changed spell; Stinking Cloud
  (22) +4 = 41h (game's 61h), Solid Fog +4..+8 `3101003c00` (game `100000f1d8`), Minor Spell Turning
  `1003003c00`, Cause Fear +4 41h, Quicksand `1001` and +1Fh A0h, Pebble +1Ch `081f06`, Magical Stone
  `001904`, Ironskin +4 `1001`, Bestow Curse / Blood Flow +1Fh A1h, Flaming Sphere +12h C0h. (+11h
  of Flaming Sphere and Minute Meteors reads 40h in memory, 00h in the file: the game's own runtime
  mark, not a patch.) DSUNLOG.EXE has the DSCLOG sites: 76D73h `cd 98 78`, 79F80h `cd 98 79`, Free
  Action's handler rewritten (79406h...), its word 0882h. Those are overlay code: not in memory
  until the spell code is loaded.
- Save `fountain-user`, clicked into Pehtucl's ambush (fight_on 1). In memory: the 18 spells known
  by Lex (#0, fighter 3 / preserver, raised to 9) and Ester (#2, fighter 2 / class 3 priest, raised
  to 9), 9 slots at every level (DS:4B08h/4B11h + 1Eh x member).
- The USE screen remembers the spell level page it was last on: the LEVEL button (196,171) steps
  it (1, 2, 3...), so check the page in a shot before clicking an icon.
- **Minute Meteors** (Lex, preserver 9, on the Templar): no to-hit roll in the log, one damage roll:
  `Minute Meteors damage: 9d4 = [2 + 1 + 4 + 1 + 4 + 3 + 4 + 1 + 2] = 22 (1d4 for each caster level,
  counted up to level 10: 9)` / `Templar takes 22 from Minute Meteors, now 19/41 HP`.
- **Magical Stone** (Ester, priest 9, on the Templar): `Magical Stone damage: 3d4 = [2 + 1 + 4] = 7`
  / `Templar takes 7 from Magical Stone, now 12/41 HP`. No to-hit line.
- The priest's USE page: icons 20 apart, five a row (x 175, 195, 215, 235, 255; y 59, 79, 99),
  in spell-number order of the spells known at that level.
- **Magical Stone, more**: one casting gave **three throws** (the stone pointer stays after each;
  the turn ends after the third), each `Magical Stone damage: 3d4` (7, 7, 10 on the Templar). The
  game already made three stones of the record's dice; with the record now 3d4 that is 9d4 a
  casting, not the manual's three stones of 1d4. One priest slot of level 1 used (9 -> 8).
- **Flaming Sphere** (Lex on a figure beside him; the sphere took Lex himself): `Flaming Sphere
  damage: 2d4 = [4 + 4] = 8` / `Lex's saving throw vs Flaming Sphere (spell): d20 = 2 ... = 8, needs
  12 (75% to save) -> failed: full damage, 8`. A made save still to see. (An earlier cast at a far
  guard used a slot and logged nothing.)
- **Bestow Curse** (Ester on the Templar): `Templar's saving throw vs Bestow Curse from Ester
  (spell): d20 = 1 (natural 1) -> failed` / `Ester gives Cursed to Templar: -1 to hit`. A save is
  now rolled. ("Cursed ends on Templar" came in the same round.)
- **Stinking Cloud** (Lex on an Arena Guard beside the Templar and a Guard): `Stinking Cloud lasts 4
  rounds (caster level 9: 3 from the dice + 1 more; dice 1d4 = [3])`, `... lasts 5 rounds (... 4 from
  the dice + 1 more; dice 1d4 = [4])`, `... lasts 2 rounds (... 1 from the dice + 1 more; dice 1d4 =
  [1])`, `... lasts 3 rounds (... 2 ...)`; saves `vs Stinking Cloud (paralysis/poison/death)` rolled,
  failed ones give `Can't Attack`. 1d4+1 as wanted.
- Trouble: passto.sh's clicks "above the figure" walked Lex off on his own, and Jenna and Ester
  died (healparty.py sets HP but doesn't raise the dead: "Dead" on the USE screen).
- **Solid Fog** (Lex on the stinking-cloud group, Lex inside too): `Solid Fog lasts 11 rounds (caster
  level 9: 1 for each caster level = 9 + 2 from the dice; dice 1d3 = [2])`, `... 12 rounds (... + 3
  ...; dice 1d3 = [3])`; `Stuck on Arena Guard: can't move ...`, Stuck on Lex and the Guard too. The
  effects list: `Stuck (11 rounds)` 660 s, `Stuck (10 rounds)` 600 s: timed, not until removed.
- An unlabelled `Dice: 2d4 = [3 + 1] = 4` came in this cast's lines (2d4 is Flaming Sphere's dice:
  perhaps the far sphere cast two turns before; no target named).
- DSCLOG check: the STINK_SITE bytes `cd 98 78` found in memory once the spell overlay had run
  (linear DFAC3h); INT 98h's vector is C91B:4A0F (DSCLOG's segment C91B0h).
- **Cause Fear**, cast by the Templar on Lex: `Cause Fear lasts 4 rounds (caster level 8: 4 from
  the dice; dice 1d4 = [4])` / `Lex's saving throw vs Cause Fear from Templar (spell): ... -> failed`
  / `Templar gives Afraid to Lex`. 1d4 rounds, not the caster's 8.
- With two members dead and Lex Afraid, reloaded `fountain-user` for a cleaner run (party HP raised
  in memory this time).

### Second run (fountain-user again; party HP 200, foes 150, in memory)

- **Quicksand** (Ester, priest 9, at the Templar beside the party): no saving throw rolled; `Stuck
  on Jenna / Lex / Templar / Seneca / Ester: can't move ...`, then an unlabelled `Dice: 5d3 = [2 + 2 +
  1 + 3 + 2] = 10`. No "lasts" line. The effects list right after: every `Stuck (1 round)`, 60 s.
- Ester's level-4 icons Blood Flow and Free Action do nothing when clicked (quick or slow press; the
  name shows in the bar below), in both runs; Focus Heat's neighbour Produce Fire on the same page
  gives the aiming pointer at once. Ironskin's icon gives the pointer, but a click on Ester's own
  figure passed her turn with no cast (slot kept).
- Lex Stuck in the quicksand: his turn opened with the END menu up; Escape closed it, then USE (24,17)
  opened.
- **Minor Spell Turning** (Lex on himself; no aiming, cast at the icon's click): `Spell Turning on
  Lex: turns spells cast at it back on their caster, one per charge`; effects list a round later:
  `Spell Turning (26 rounds)`, 1560 s, charges None (3 x 9 = 27 rounds less the one gone).
- Quicksand: `Stuck ends on Lex, Jenna, Ester, Seneca, Templar, Guard` at the end of round 1 (a
  round after the cast); the quicksand's picture stays on the floor.
- **Cause Fear** (Ester on the Templar): `Cause Fear lasts 1 round (caster level 9: 1 from the dice;
  dice 1d4 = [1])` / save rolled and made. The Templar answered with `Cause Fear lasts 2 rounds
  (caster level 8: 2 from the dice; dice 1d4 = [2])` on Ester (saved).
- Harmful spells can't be aimed at the party: `Ester can't cast Cause Fear there: not a creature
  that spell can be cast on` (on Lex). So Minor Spell Turning needs a foe casting at the turner.
- Quicksand does keep sticking: `Stuck on Templar` again at his turn in round 2 (the patch is on).
- **Chaos, normal INT** (Lex at the Templar; the fight's Templar turned out to be creature 30, INT 12,
  WIS 17, class 19: the INT 22 written into creature 11 went to another Templar): `Templar's saving
  throw vs Chaos from Lex (spell): none allowed (cannot save) -> failed` (normal INT, not a warrior:
  no save, as wanted). The party (all with warrior classes) rolled normal saves: `Jenna's saving
  throw vs Chaos from Lex (spell): d20 = 5 +4 WIS 20 = 9, needs 16 ... -> failed` / `Lex gives
  Confused to Jenna`; Seneca, Ester failed, Lex natural 20.
- Creature 30's INT then set to 22 in memory for the next Chaos.
- **Chaos, INT 22** (same Templar, creature 30's INT written 22): `Templar's saving throw vs Chaos
  from Lex (spell): d20 = 6 +1 Ring of Protection +3 WIS 17 = 10, needs 12 (65% to save) -> failed`:
  a normal save, rolled (CHAOS_SITE at work).
- **Quicksand's length**: `Stuck on ...` lines came in every round from the cast (round 1) to
  round 11, and none in round 12 (`Stuck ends on Lex, Templar` at the end of round 11). Each Stuck
  effect is 1 round (60 s), put on again while the creature stands in it. The unlabelled `Dice: 5d3 =
  10` after the cast would fit a 10-round lifetime (from mid-round 1 to mid-round 11); 1 round a
  level (9) would have ended a round sooner. Not settled which.
- Ester's spell icons were all **crossed out** in a turn she was hit just before ("YOU WERE HIT" in
  the bar): no spell that turn; next round they were plain (spell disruption, it seems).
- **Touch spells in a fight target a portrait on the USE screen**, not a figure: Ironskin's icon
  click left the screen up (no aiming pointer); a click on Jenna's portrait (112,62) cast it. (Free
  Action and Blood Flow "doing nothing" in the first run were surely the same: their icons wait
  for a portrait.)
- **Ironskin** (Ester, priest 9, on Jenna): `Ester gives Ironskin to Jenna: no damage from weapons,
  using up one charge each time`, then at once, at Seneca's turn and with no blow struck: `Ironskin
  ends on Jenna`. The effects list showed no Ironskin. Expected 9 charges.
- **Ironskin again** (Ester on herself, portrait 66,108), effects read within half a second:
  `Effect(owner=2, caster=2, id=53) charges None secs 0 | Ironskin (0 rounds)`: the effect's charge
  byte (+8) 0 and an end event due at once; then `Ironskin on Ester: ...` / `Ironskin ends on Ester`
  at the next turn. **Ironskin now gets no charges at all**: the record's per-level byte (+5, 01)
  isn't counted for a spell counted in charges (unit -1), and its dice (+4 = 10h, 0 dice) give 0.
  The game's 1d6 (61h) had given 1-6. (MST and Solid Fog, counted in rounds, did take +5.)
- **Turn Pebble Into Boulder** (Lex on an Arena Guard): `Turn Pebble Into Boulder damage: 3d6 = [1 +
  3 + 5] +8 = 17` / `Arena Guard takes 17 ..., now 12/150 HP`. 3d6+8 as wanted.
- **Flaming Sphere, made save** (Lex at an Arena Guard two squares off; again only Lex was caught):
  `Flaming Sphere damage: 2d4 = [1 + 1] = 2` / `Lex's saving throw vs Flaming Sphere (spell): d20 =
  11 +1 Ring of Protection +5 DEX 21 dodging = 17, needs 12 (75% to save) -> saved: no damage (not
  2)`. No damage on a made save, as wanted. (Both spheres that logged anything struck the caster,
  not the guard clicked; those cast farther off used a slot and logged nothing.)
- **Blood Flow** (Ester; its icon too waits for a portrait: cast on Jenna's, 112,62, since harmful
  spells can be put on the party that way): `Blood Flow lasts 2 rounds (caster level 0: 2 from the
  dice; dice 1d4 = [2])` / `Jenna's saving throw vs Blood Flow from Ester (spell): d20 = 1 (natural 1)
  -> failed` / `Blood Flow: 2d6 = [2 + 4] = 6`. A save is now rolled. (The lasts line's "caster level
  0" is the Loader's reading, worth a look.)
- Solid Fog cast over the party (to have someone Stuck): `Solid Fog lasts 10/11/12 rounds (caster
  level 9: 1 for each caster level = 9 + N from the dice; dice 1d3 = [N])`, all four Stuck.
- **Free Action on a Stuck member** (Ester, portrait of Jenna): `Ester gives Free Action to Jenna:
  can't be Paralyzed, Slowed or Stuck` / `Stuck ends on Jenna`. Freed, as wanted. Effects:
  `Free Action (9 rounds)` on Jenna.
- A Stuck member's turn opens with its END menu up: E ends the turn; Escape closes it to act.
- Paralysis made in memory (Hold Person is an aimed spell and refused on the party's figures): the
  Stuck effects of Seneca and Lex rewritten to Paralyzed (id 34, spell 86) by
  `/tmp/playtest/conv.py`; the Loader saw it (`Paralyzed on Seneca: loses its turns ...`), and
  Lex's next turn was skipped.
- **Remove Paralysis** (Ester, level 3, icon 212,97, Seneca's portrait): `Paralyzed ends on Seneca`.
  Still works.
- Ester's Stuck rewritten to Slowed (47): `Slowed on Ester: -4 to hit, ...` and her initiative `-2
  Slowed`.
- **Free Action on Slowed** (Ester on herself, portrait 66,108): `Free Action on Ester: can't be
  Paralyzed, Slowed or Stuck` / `Slowed ends on Ester`.
- **Free Action on Paralyzed** (Ester, Lex's portrait 66,62): `Ester gives Free Action to Lex: ...` /
  `Paralyzed ends on Lex`. All three of the handler's ways work.
- **Minor Spell Turning, try 1**: Blood Flow (priest 4, a portrait spell) from Ester on Lex, with
  `Spell Turning (8 rounds)` on him: not turned. `Lex's saving throw vs Blood Flow from Ester (spell):
  d20 = 12 +1 Ring of Protection = 13, needs 12 (50% to save) -> saved`, `Dice: 2d6 = [3 + 3] = 6`
  (no "takes" line). Spell Turning still on him after.
- Harmful aimed spells (Cause Light Wounds too) are refused on the party's figures, and no 1st-3rd
  level harmful spell is a portrait spell (record +0Ch 3, 5, 7), so the turning was tried with a
  helpful one.
- **Minor Spell Turning, turn 1**: Ester's Cure Light Wounds (priest 1) on Lex's portrait, Lex at
  150 HP and Spell Turning on him: `Cure Light Wounds: 1d8 = [7] = 7` / `Ester regains 7 HP from Cure
  Light Wounds, now 157/200 HP`: turned back on the caster. Spell Turning still listed afterwards
  (`Spell Turning (6 rounds)`).
- **Minor Spell Turning, turn 2** (next round, same again): `Cure Light Wounds: 1d8 = [7] = 7` /
  `Ester regains 7 HP from Cure Light Wounds, now 164/200 HP`; `Spell Turning (5 rounds)` still on
  Lex. **It turns more than one spell**: every 1st-3rd level spell aimed at the turner for its whole
  time (the effect's charge byte is 0 and isn't used up). Blood Flow (4th) wasn't turned (the game's
  level limit).

### Third run: the switch off, to compare (Quicksand, Magical Stone, Ironskin)
- Switch off (`spells_manual` False written with launch.save_settings, then loadsave.sh): the records
  in memory are the game's own (Quicksand +4 11h +1Fh A1h, Magical Stone 0904h, Ironskin 61h).
- **Ironskin, switch off** (Ester on herself): `Effect(owner=2, caster=2, id=53) charges 6 secs None |
  Ironskin (6 charges)`, `Dice: 1d6 = [6] = 6`, and it stays. So with the switch on the 0 charges are
  the patch's doing.
- **Magical Stone, switch off** (Ester at the Templar): three throws from one casting again, each
  `Magical Stone damage: 1d4 = [4] = 4`, `1d4 = [2]`, `1d4 = [1]`; one level-1 slot used. So the
  game already had the manual's three 1d4 stones; with the switch on each stone is 3d4 (9d4 a
  casting).
- **Quicksand, switch off** (Ester at the Templar): `Quicksand lasts 1 round (caster level 0: 1 from
  the dice; dice 1d1)`, `Quicksand: 5d3 = [2 + 3 + 2 + 3 + 2] = 12`, saves rolled (`Jenna's saving
  throw vs Quicksand (spell): d20 = 16, needs 16 -> saved`, the rest failed), Stuck 1 round each.
  So the 5d3 roll (unlabelled `Dice: 5d3 = 10` with the switch on) is the quicksand's own lifetime
  in rounds, the same either way, and the Stuck it gives is 1 round, put on again each round; the
  Loader reads the caster level of a spell left on the ground as 0. With the switch on the save is
  gone (as wanted), but "1 round a caster level" shows nowhere: each Stuck was still 1 round, and the
  quicksand lasted its 5d3 rounds. The record's per-level time seems unused here (the ground's
  "caster" has level 0).
- The switch put back afterwards (the `spells_manual` key removed: reads None, on).
