# 2026-11-20: F10 after a spell, and after a pin (2.19.0's mend)

**Under test**: 2.19.0's "F10 takes a whole move back" (`dsloader/moveback.py`,
`DiceLog._move_back_pass`, setting `move_back`; [the developer
notes](../../obsidian-edition/DEVELOPMENT-SCREENS.md#f10-takes-a-whole-move-back)). The mend must
give the walk back after the last step, and never after an attack, a spell or an effect that pins
the member. The release left "F10 after a spell cast, and after an effect that pins a member" not
seen in the game ([2026-11-18](2026-11-18-modernisation-features.md)): this play is that check.

**Build**: `origin/obsidian-edition` at 1677df3 (2.19.0 and two doc PRs), branch
`claude/f10-after-spell`. DOSBox 0.74-3, window 320x240, `buildcheck.py` OK. `settings.json`:
`move_back` true, `autosave` false, `quick_save` false, written before the fight and the dice log
restarted. Save `fountain-user`, `dismiss.sh` into Pehtucl's ambush.

**How it was read**: `f10watch.py MEMBER SECONDS` (new, in the kit) in the background through each
turn: whose turn, the member's flags (37BD:01D5h, bit 0 "can walk"), points (+22Bh), swings
(+181h), commands (+1ABh), square, and the turn's start words DS:4964h/4966h/4968h (points, y, x).
Walks by `squarewalk.py COL ROW` with no POINTS (no edit), `movestate.py` before and after.

## Results

| Case | What the game did on F10 | Flags / points after | Loader | Right? |
|---|---|---|---|---|
| 1a. Last step, then Curse (Ester) | the cast ended her turn at once; F10 was the next member's | 0 / 0, Ester stays put | nothing | yes |
| 1b. Last step, then Magical Stone, one throw (Ester) | the turn stays hers (two throws left); F10 put her back on the turn's first square with 120 points | **0** / 120 | nothing | yes |
| 2a. Walk partway, then Reflected Image (Lex) | the cast ended his turn (90 points unused); F10 the next member's | 0 / 90, Lex stays put | nothing | yes |
| 2b. Walk partway, then Magical Stone, one throw (Ester) | put back on the first square with 120 points | **0** / 120 | nothing | yes |
| 3. Control: plain last step (Seneca, twice) | put back with 120 points | 3EEh then **3EFh** 20 ms later / 120 | `F10: Seneca's move taken back (can walk again)`; she walked | yes |
| 4. Last step, then Paralyzed **by a memory edit**, then F10 (Seneca) | put back with 120 points | 3EEh then **3EFh** / 120 | **`F10: Seneca's move taken back (can walk again)`** | **no**: see below; [fixed](#the-fix-played) |
| (4b. Held by the Templar's real Hold Person: Lex) | his turns never came (no "Lex's turn" in rounds 2 and 3) | - | - | nothing to F10 |

**A spell cast zeroes the whole flags word** (37BD:01D5h = 0), whether movement is left or not, so
the mend's "same flags" never holds after a cast and it stays out. Most spells end the turn with it;
Magical Stone (several throws a casting) keeps the turn with the flags at 0, and the game's F10
then still moves the caster back and restores the points, but with the flags 0 no click walks.

**The pin after the last step was a gap** (reported first, then fixed with the user's approval: [the fix, played](#the-fix-played)): the effect routine that pins
(DSUN.EXE 786A9h-786CBh: effects 22h and 33h) only does `and word es:[bx+1D5h], 0FFFEh`, and after
the last step bit 0 is already clear, so the flags stay exactly as the last step left them. The mend
then sees FULL, SPENT and F10's points as in case 3 and gives the walk. In the game the paralysed
Seneca walked one step (10 points) and then the game zeroed her flags and passed the turn: one
square of movement for a held member. The pin here was a record put in the effect table by
`addeffect.py 3 34`, not the game's routine; the routine would have changed nothing more (the bit
already clear). Whether a pin can land on a party member during its own turn after its last step
in play (an area effect entered on the last step, say) was not looked for.

## Run 1 (no memory edit)

- **Case 1a**, Ester at (54,95), 120 points, flags 3EFh: `squarewalk.py` (56,89) 52 left, (56,93)
  12, (57,93) 0: flags 3EEh, the END menu (closed with Escape by the tool). U, Curse (194,59), the
  Templar (`foepos.py` 240,134; clicked 6 above):
  ```
      Curse lasts 6 rounds (caster level 3: 6 from the dice; dice 6d1)
  Ester gives Cursed to Templar: -1 to hit
  Jenna's turn
  ```
  f10watch:
  ```
  12.98 turn 2 flags 0x3ee points 0 ... sq (56, 93) start (120, 1528, 872)
  13.01 turn 2 flags 0x3ee points 0 ... sq (57, 93) start (120, 1528, 872)
  41.43 turn 2 flags 0x0 points 0 ... sq (57, 93) start (120, 1528, 872)
  41.48 turn 1 flags 0x0 points 0 ... sq (57, 93) start (120, 1528, 872)
  41.56 turn 1 flags 0x0 points 0 ... sq (57, 93) start (140, 1528, 904)
  ```
  F10 on Jenna's turn (she hadn't moved): nothing changed; Ester (57,93), flags 0, points 0; no
  Loader line.
- **Case 2a**, Lex at (55,94), 120: walked to (52,94), 90 left, 3EFh. U: his page is Shocking
  Grasp (176,59), Erdlu Claw (194), Reflected Image (212), Friends (230). Reflected Image (a self
  spell, cast at the icon's click):
  ```
      Reflected Image has 1 charge (caster level 2: 1 from the dice; dice 1d1)
  Mirror Images on Lex: each hit, and each foe's spell for one creature, has a 75% chance (50% for Reflected Image's) to strike an image instead, which vanishes
  Seneca's turn
  ```
  f10watch: `39.63 turn 0 flags 0x0 points 90 sq (52, 94)`, then turn 3. F10 on Seneca's turn:
  nothing; Lex stays (52,94); no Loader line.
- **Case 3**, Seneca at (55,96), 120: (49,96) 60, (49,92) 20, (47,92) 0, flags 3EEh. F10:
  ```
  14.46 turn 3 flags 0x3ee points 120 ... sq (55, 96) start (120, 1544, 888)
  14.48 turn 3 flags 0x3ef points 120 ... sq (55, 96) start (120, 1544, 888)
  ```
  `F10: Seneca's move taken back (can walk again)`; `movestate.py` marked the squares again; a click
  on (53,96) walked her there (100 left).
- Then `passuntil.sh 2` for Ester's next turn: the Templar's Hold Person had paralysed Ester, her
  turn never came, and passuntil passed turns until the party was defeated (the watchdog's STUCK on
  "YOUR PARTY HAS BEEN DEFEATED"). Reloaded.

## Run 2 (memory edits from here: every foe Paralyzed, nothing saved)

`dismiss.sh`, then `foeset.py C eff=34` for 17-47 (41 and 44 aren't combatants). The Templar's Hold
Person had already landed on Lex (`Lex's saving throw vs Hold Person from Templar (spell): d20 = 1
(natural 1) -> failed`); his turns never came in rounds 2 and 3, so the real pin gives no turn to
press F10 in (4b).

- **Case 4**, Seneca, the same three walks: (47,92), 0 points, 3EEh. `addeffect.py 3 34` (Paralyzed
  on her, untimed; the dice log: `Paralyzed on Seneca: loses its turns, can't move, fails every
  saving throw`); flags still 3EEh, points 0 ([picture](img/2026-11-20-f10-after-spell-pinned-spent.png)).
  F10 ([picture](img/2026-11-20-f10-after-spell-pinned-f10.png)):
  ```
  25.89 turn 3 flags 0x3ee points 120 ... sq (55, 96) start (120, 1544, 888)
  25.91 turn 3 flags 0x3ef points 120 ... sq (55, 96) start (120, 1544, 888)
  ```
  `F10: Seneca's move taken back (can walk again)`, the squares marked round her. A click on
  (53,96):
  ```
  34.21 turn 3 flags 0x3ef points 110 ... sq (55, 96)
  34.27 turn 3 flags 0x3ef points 110 ... sq (54, 96)
  34.32 turn 3 flags 0x0 points 110 ... sq (54, 96)
  34.37 turn 2 flags 0x0 ...
  ```
  One step while Paralyzed, then the game ended her turn. `addeffect.py del 3 34` after.
- **Case 1b**, Ester (54,95), 120: the same walks to (57,93), 0 points, 3EEh.
  `spellsetup.py 2=9` (a memory edit: Magical Stone taught, her priest level 9; without it her
  level-1 page is Bless 176,59, Curse 194, Cure Light Wounds 212, Cause Light Wounds 230, Entangle
  248; Invisibility to Undead 176,79, Protection from Evil 194, Remove Fear 212, Cause Fear 230).
  U, Magical Stone (194,79), the Templar (256,128):
  ```
  Magical Stone damage: 1d4 = [2] = 2
  Ester's Magical Stone at Templar: attack d20 = 7, needs 11+ (50%) (THAC0 19, +4 DEX; target AC 4) -> MISS: the spell does nothing, the 2 damage rolled lost
  ```
  The stone pointer stayed up ([picture](img/2026-11-20-f10-after-spell-stone-thrown.png)). F10
  ([picture](img/2026-11-20-f10-after-spell-stone-f10.png): back by the others, the panel "Move :
  12"):
  ```
  62.85 turn 2 flags 0x3ee points 0 ... sq (57, 93) start (120, 1528, 872)
  86.17 turn 2 flags 0x0 points 0 ... sq (57, 93) start (120, 1528, 872)
  99.04 turn 2 flags 0x0 points 120 ... sq (54, 95) start (120, 1528, 872)
  ```
  No Loader line; `movestate.py` marked no square (flags 0). The stone pointer was still up: the two
  throws left went from the new square (both missed), the turn passed after the third.
- **Case 2b**, Ester's next turn: (54,95) to (54,92), 90 left, 3EFh. Magical Stone at the Templar:
  `-> HIT`, `Templar takes 4 from Magical Stone (Paralyzed: the most the dice can do)`. F10:
  ```
  189.95 turn 2 flags 0x0 points 90 ... sq (54, 92) start (120, 1528, 872)
  193.55 turn 2 flags 0x0 points 120 ... sq (54, 95) start (120, 1528, 872)
  ```
  No Loader line. A right-click cancelled the aim and passed the turn.

**Nothing saved**: no autosave or quick save in either run (the folder's `SAVQ*` files are older);
DOSBox and the dice log stopped by their pids.

## The fix, played

The user approved a fix: `moveback.py` now reads the member's effects at F10 (`GameData.effects()`,
owner its combatant) and writes nothing with 34 (Paralyzed) or 51 (Stuck) on it, the two effects
whose landing clears the bit (786A9h-786CBh: `cmp [bp+0Ah], 22h` / `33h`, then `and word
es:[bx+1D5h], 0FFFEh`; only 591BCh and 786CBh have that instruction). A unit test
(`test_not_for_a_member_pinned_after_the_last_step`) holds the state seen here; it fails with the
check taken out.

Played on the fixed Loader (`loadsave.sh fountain-user` with the change in the tree; the dice log
started with it; autosave and quick save off; every foe Paralyzed as in run 2; nothing saved):

- **Case 4 again**, Lex at (55,94), 120 points: (49,94) 60, (49,92) 40, (49,96) 0, flags 3EEh.
  `addeffect.py 0 34` (`Paralyzed on Lex: ...`), flags still 3EEh. F10
  ([picture](img/2026-11-20-f10-after-spell-fixed-pinned-f10.png)):
  ```
  15.01 turn 0 flags 0x3ee points 0 ... sq (49, 96) start (120, 1512, 888)
  22.36 turn 0 flags 0x3ee points 120 ... sq (55, 94) start (120, 1512, 888)
  ```
  No Loader line, no squares marked; a click on (53,93): `NOT REACHED`, 120 points, Lex unmoved.
  With the effect taken off again (`addeffect.py del 0 34`) the flags stayed 3EEh: the turn's
  sequence was forgotten, so nothing is given later either.
- **The control again**, Jenna at (56,95), 140 points: (56,88) 70, then toward (57,95): (57,94),
  0 points, 3EEh. F10:
  ```
   9.65 turn 1 flags 0x3ee points 140 ... sq (56, 95) start (140, 1528, 904)
   9.66 turn 1 flags 0x3ef points 140 ... sq (56, 95) start (140, 1528, 904)
  ```
  `F10: Jenna's move taken back (can walk again)`; a click on (58,93) walked her there (112 left).

The suite with `-W error` (`/usr/bin/python3.12`): 2,186 tests, OK, 56 skipped without the game's
files; 2,186, OK, none skipped with `DSUN_OBJECTS`, `DSUN_GPLDATA` and `DSUN_RESOURCE` set. DSCLOG
untouched.

## Learned

- A spell cast zeroes the turn flags; most casts end the turn, Magical Stone's doesn't until the
  third throw, and the game's F10 then moves the caster back with its points but no walk.
- The game's F10 doesn't look at effects: it moved a Paralyzed member back with its points.
- A Paralyzed party member's turn is skipped whole (Lex, by Hold Person), and `passuntil.sh N` for
  that member then passes turns until the fight is lost.
- Three of four Magical Stones missed the Paralyzed Templar: a spell's attack roll is rolled
  against a held target (only weapons hit held targets automatically), and a hit does the most
  the dice can.

Water: none new (the fountain and Lex's Pot of Water in `fountain-user` are in ROUTE.md already).
