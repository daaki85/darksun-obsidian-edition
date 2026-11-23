# Test log: Wake of the Ravager's weapons in Shattered Lands (2026-11-23)

Branch `claude/sl-ravager-weapons`: the sequel's seven weapon kinds the game has none of (a
two-handed sword, the lotulis, the double spear, the trikal, the javelin, darts and, at first, a
net, which the user then left out), six weapon specs for them, and the traits of the lotulis, double spear and trikal. DOSBox
with the Loader's patched game, the window 320x240, `buildcheck.py` OK before each play. Each step
has a control run on `origin/obsidian-edition` (a worktree; its own `playtest/loadsave.sh`, so its
own DSCLOG). Every change below was in memory; nothing was saved (`"autosave": false`,
`"quick_save": false`).

## 1. The weapon window (creation screen)

- New game, CREATE CHARACTERS, NEW (a human fighter), DONE: the window showed only 16 slots at first,
  the kit pages' row buttons (870h on) sharing the new slots' ids (870h-875h). Moved the slots to
  8C0h: all 22 show, four rows of six with two to spare (layout A).
- The title (PICK A WEAPON SPECIALTY, name) was missing at first: the game's "push 46h" takes a
  signed byte and row four's title line is at 146. Now the game draws no lines and PK_HOVER puts the
  title at once. Control run (origin/obsidian-edition): three rows, the title under them.
- A fighter: the double spear and trikal greyed (gladiators only, as in Ravager); lotulis picked:
  "starts with a plain stone lotulis". A gladiator: all 22 in use; trikal then double spear picked:
  specs ['trikal', 'double spear'], "starts with a plain wooden trikal" (the first pick kept first:
  the first try of the new layout sorted the picks, and the double spear came first; the layout was
  remade, v3, to keep it).
- `fountain-user` (a save from before, the specs in the v2 layout): Jenna's and the others' specs
  read as before (`sheetinfo.py`, the Effects screen's SPECIALIZED IN).

## 2. The traits in a fight (`fountain-user`, the slave pens' ambush)

Set up in memory: Jenna (member 1) a gladiator (`kitset.py 1 10 5 0`, later `sheetedit.py 1
level0=9` and the sheet's +2Ah 4, two attacks a round), her specs written with the new
`specset.py` (lotulis and trikal; then double spear and trikal; then trikal and double spear), her
item 115 made each weapon in turn (`setitem.py 115 rec=...`, the record from
`worldgear.weapon(worldgear.LOTULIS)` and the like: type 149 has no SEGOBJEX record, so `setitem.py
115 149` finds none). Two foes put beside her (`placefoe.py`, a scratch tool writing DS:669Dh + 20h
x thing) and held (`foeset.py N eff=34`), then Tab to the held one and Return.

- **The lotulis: hits, and the large dice.** `Jenna attacks Guard with Stone Lotulis (1d10) ... hits
  for 12: 1d12 = [3] -1 stone +2 specialized (1d12 for 1d10: a large target) +8 STR 20`: the
  half-giant Guard large, +1 to hit and +2 damage specialized.
- **Only one swing at first, twice over.** Her second attack was her Bone Long Sword in the other
  hand: moved to slot 20 it was still worn (slot 20 is in the worn list, `carried.py` list 0xA), so
  it was made a Wind Potion (`setitem.py 24 60`). Then the lotulis itself swung once a round:
  it was in the left hand (slot 10), and the off hand attacks once a round whatever the rate
  ([two weapons](../../obsidian-edition/FEATURES.md#two-weapons)). Moved to the right hand
  (`itemedit.py 1 10 slot=3`) with +2Ah 4 it swung twice.
- **The lotulis' second foe.** `Jenna hits Guard for 14 ... / Jenna turns the lotulis's last swing
  from Guard to Guard, beside it (a specialist's second foe) / Jenna attacks Guard with Stone
  Lotulis ... hits for 19 / Guard now 19/50 HP (-14) / Guard now 0/50 HP (-6) / Guard is killed`:
  the first swing on the Guard at 33 HP, the last on the other Guard (6 HP) beside her.
- **The double spear's second foe, 1 less.** `Jenna hits Arena Guard for 14: 1d8 = [4] +2
  specialized +8 STR 20 / Jenna turns the double spear's last swing from Arena Guard to Arena Guard,
  beside it (a specialist's second foe, 1 less damage) / ... hits Arena Guard for 15: 1d8 = [5] ... /
  Arena Guard now 16/30 HP (-14: 14 of the 15 rolled)`: the second Arena Guard took 1 less than
  rolled. The hit line still said 15 (the dice log reads the damage before SF_LESS takes the 1):
  fixed, the line now ends `-1 second head` with the right total (`test_second_head_damage`).
- **The trikal's trip.** Against a free Arena Guard (its hold taken off, its HP made 200 so the hit
  doesn't fell it): `Jenna hits Arena Guard for 15: 1d10 = [5] +2 specialized +8 STR 20 / Jenna's
  trikal trips Arena Guard? Save against paralysis: d20 = 12, needs 13+ -> tripped: loses its next
  turn`. (The first try felled its target, 16 HP: no trip line, as for the cahulaks.) The lost turn
  is the cahulaks' tangle's own (`SWEPT_NOW`, `FAR_SWEPT`), played and logged before; here every foe
  near was an "Arena Guard", so the log can't say which one acted next.
- **Control run** (origin/obsidian-edition, the same save, Jenna a gladiator 9 at two attacks a
  round, the Bone Long Sword in the right hand, two held Guards beside her): both swings on the
  same Guard (`Guard now 29/50 HP (-21)`, `Guard now 13/50 HP (-16)`), no second foe.

## 3. The trikal's lost turn, one foe told apart (the coordinator's ask)

The trip line came up in section 2, but every foe near was an "Arena Guard", so the turn it lost
couldn't be seen. Played again from `fountain-user`, the same set-up (Jenna a gladiator 9, two
attacks a round, the trikal her weapon spec, in her right hand), and one Arena Guard (combatant 34)
named apart and kept up: `foeset.py 34 name=Tripme hp=200` (`name=` new in foeset.py), put beside
her (`placefoe.py 34 1 0 1`), not held.

- Round 1: `Jenna hits Tripme for 15: 1d10 = [5] +2 specialized +8 STR 20 / Jenna's trikal trips
  Tripme? Save against paralysis: d20 = 2, needs 13+ -> tripped: loses its next turn`.
- Round 2: `Round 2: Tripme 29, Guard 28, Arena Guard 26, Arena Guard 23, Arena Guard 22`: Tripme
  first of the foes, and **no "Tripme's turn"** in the round: the Guard's, three Arena Guards' and
  the Templar's turns, then Round 3.
- Rounds 3 and 4: `Tripme's turn`, each time shooting at Ester with its bow (`Tripme attacks Ester
  with Wooden Bow (1d8) ...`): it acts again once the turn is lost.

The net was taken out afterwards (the user's call). The build without it: `buildcheck.py` OK,
`fountain-user` loads, and an item made darts (`setitem.py 115 rec=...`) reads "Wooden Darts", type
153, its name entry 377 (0x179), as before.

## What was learned (in the guide)

- A member with no Move left at the start of a turn gets the END menu at once, and a Tab + Return
  loop waits on it for ever: click the figure (`memberpos.py N`, then `click.py`) and press E
  there (END TURN). With nothing open E is the Effects screen.
- A weapon in the left hand (slot 10) swings once a round, whatever the rate: put the weapon under
  test in the right hand (slot 3).
- Slot 20 is still worn: to take a weapon out of the hands for a test, make it something else
  (`setitem.py N 60`).
- A sheet's address moves with the build (DSCLOG's size moves DS): read it from `sheetedit.py`
  before writing to it, every load.
- `specset.py MEMBER KIND...` writes a member's weapon specs in memory, the first kept first.
- `foeset.py C name=S` names one foe apart, so the dice log shows its turns (and the ones it loses).

No new area: no water to note.
